import os
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from StringIO import StringIO

from postcode_api.downloaders.local_authorities_downloader import LocalAuthoritiesDownloader
from postcode_api.importers.local_authorities_importer import LocalAuthoritiesImporter
from postcode_api.utils import ZipExtractor

class Command(BaseCommand):
    args = '<destination_dir (default /tmp/)>'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--destination_dir', 
                action='store_true', 
                dest='destination_dir',
                default='/tmp/local_authorities/')

        # Named (optional) arguments
        parser.add_argument('--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force download even if previous download exists')

    def handle(self, *args, **options):

        if not os.path.exists(options['destination_dir']):
          os.makedirs(options['destination_dir'])

        downloaded_file = self.__download(options['destination_dir'], options.get('force', False) )
        if downloaded_file:
            return self.__process(downloaded_file)
        else:
            print 'nothing downloaded - nothing to import'
            return None

    def __download(self, destination_dir, force=False):
        print 'downloading'
        downloader = LocalAuthoritiesDownloader()
        return downloader.download(destination_dir, force)

    def __process(self, filepath):
        files = ZipExtractor(filepath).__unzip_if_needed('*.nt')

        for path in files:
            print 'importing ' + path
            result = self.__import(path)
            self.__cleanup(path)

        self.__cleanup(filepath)

    def __import(self, downloaded_file):
        importer = LocalAuthoritiesImporter()
        importer.import_local_authorities(downloaded_file)

    def __cleanup(self, downloaded_file):
        print 'removing local file ' + downloaded_file
        os.remove(downloaded_file)
