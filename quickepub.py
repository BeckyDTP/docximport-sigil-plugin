# -*- coding: utf-8 -*-
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import unicode_literals, division, absolute_import, print_function

import os
import textwrap
from uuid import uuid4

from epub_utils import epub_zip_up_book_contents

CONTAINER = textwrap.dedent('''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="{0}" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>''')

OPF = textwrap.dedent('''<?xml version="1.0" encoding="utf-8"?>
<package version="{0}" unique-identifier="BookId" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId" opf:scheme="UUID">urn:uuid:{1}</dc:identifier>
    <dc:language>en</dc:language>
    <dc:title>[No data]</dc:title>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="Section0001.xhtml" href="Section0001.xhtml" media-type="application/xhtml+xml"/>
    {2}
    {3}
  </manifest>
  <spine toc="ncx">
    <itemref  idref="Section0001.xhtml"/>
  </spine>
  <guide>
  </guide>
</package>''')

NCX = textwrap.dedent('''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
   "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head>
   <meta name="dtb:uid" content="urn:uuid:{0}" />
   <meta name="dtb:depth" content="0" />
   <meta name="dtb:totalPageCount" content="0" />
   <meta name="dtb:maxPageNumber" content="0" />
</head>
<docTitle>
   <text>Unknown</text>
</docTitle>
<navMap>
<navPoint id="navPoint-1" playOrder="1">
  <navLabel>
    <text>Start</text>
  </navLabel>
  <content src="Section0001.xhtml" />
</navPoint>
</navMap>
</ncx>''')

IMG = '<item id="{0}" href="Images/{0}" media-type="{1}"/>'
CSS = '<item id="css" href="stylesheet.css" media-type="text/css"/>'

class QuickEpub(object):
    def __init__(self, temp_dir, outdir, htmlfile, version, img_map, cssfile=None):
        self.outdir, self.htmlfile, self.version, self.img_map, self.cssfile = outdir, htmlfile, version, img_map, cssfile
        self.uid = uuid4()
        self.epubname = os.path.join(temp_dir,'new.epub')
        self.img_items = self.manifest_images()
        self.opffile = self.make_opf()
        self.metainf = self.make_metainf()
        self.ncxfile = self.make_ncx()

    def make_metainf(self):
        metainf = os.path.join(self.outdir,'META-INF')
        if not os.path.exists(metainf):
            os.mkdir(metainf)

        containerdata = CONTAINER.format(os.path.basename(self.opffile))
        fileout = os.path.join(metainf,'container.xml')
        open(fileout,'wb').write(containerdata.encode('utf-8'))
        return metainf

    def make_opf(self):
        opffile = os.path.join(self.outdir,'content.opf')
        cssmanifest = ''
        if self.cssfile is not None:
            cssmanifest = CSS
        opfdata = OPF.format(self.version, self.uid, self.img_items, cssmanifest)
        open(opffile,'wb').write(opfdata.encode('utf-8'))
        return opffile

    def make_ncx(self):
        ncxfile = os.path.join(self.outdir,'toc.ncx')
        ncxdata = NCX.format(self.uid)
        open(ncxfile,'wb').write(ncxdata.encode('utf-8'))
        return ncxfile

    def manifest_images(self):
        img_dir = os.path.join(self.outdir,'Images')
        items = ''
        if os.path.exists(img_dir) and os.path.isdir(img_dir) and self.img_map is not None:
            for fname, mtype in self.img_map.items():
                if os.path.isfile(os.path.join(img_dir, fname)):
                    items += IMG.format(fname, mtype) + '\n'
        return items

    def makeEPUB(self):
        # add the mimetype file uncompressed
        mimetype = 'application/epub+zip'
        fileout = os.path.join(self.outdir,'mimetype')
        open(fileout,'wb').write(mimetype.encode('utf-8'))

        epub_zip_up_book_contents(self.outdir, self.epubname)

        return self.epubname
