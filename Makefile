BINPATH = .

all: herd-mapping.json

mapping.wiki:
	./extract-wiki-text.py 'https://wiki.gentoo.org/index.php?title=Project:Metastructure/Herd_to_project_mapping&action=edit' > $@

mapping.names: mapping.wiki
	./wiki2names.py $< > $@

herds.xml:
	wget -O $@ https://api.gentoo.org/packages/herds.xml

projects.xml:
	wget -O $@ https://api.gentoo.org/metastructure/projects.xml

herd-mapping.json: mapping.names herds.xml projects.xml
	./get-merged-mappings.py $+ > $@

clean:
	rm -f mapping.wiki mapping.names herds.xml projects.xml herd-mapping.json
