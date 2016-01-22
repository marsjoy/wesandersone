#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Retrieves dominant colors for film stills using web scraping and color math
import logging
import os

from wesandersone.utilities import command
from wesandersone.utilities.arguments import Arguments
from wesandersone.utilities.color import hex_to_rgb, hsl_from_lab, hsv_from_lab, lab_from_rgb
from wesandersone.utilities.writer import save_row
from wesandersone.workflows.base_etl_workflow import BaseETLWorkflow
from wesandersone.workflows.color_scraper.color_scraper import ColorScraper

logger = logging.getLogger(__name__)


class ColorScraperWorkflow(BaseETLWorkflow):

    def __init__(self,
                 movies=None,
                 director=None):
        super(ColorScraperWorkflow, self).__init__(workflow_name='color_scraper')
        self.movies = movies
        self.director = director
        self.image_path = self.config.path.get('source_data', None)
        self.file_name = 'extracted_colors'
        self.base_dir = str()
        self.file = str()
        self.compressed_file = str()
        self.set_up()
        self.extracted_colors_path = '{file}_' \
                                     '{director}.csv'.format(file=self.file,
                                                             director=director)

    def set_up(self):
        self.base_dir, self.file, self.compressed_file = self.get_file_path()
        command.create_directories(self.base_dir)

    def extract(self):
        self.extract_colors_from_film_stills()


    def extract_colors_from_film_stills(self):
        for movie in movies:
            film_stills_path = '{image_path}/' \
                               '{director}/' \
                               '{movie}/'.format(image_path=self.image_path,
                                                 director=self.director,
                                                 movie=movie)
            for film_still in os.listdir(film_stills_path):
                film_still_path = '{film_stills_path}' \
                                  '{film_still}'.format(film_stills_path=film_stills_path,
                                                        film_still=film_still)
                self.extract_color_from_film_still(film_still=film_still_path,
                                                   movie=movie)

    def extract_color_from_film_still(self, film_still=None, movie=None):
        color_scraper = ColorScraper(image=film_still, use_firefox=True)
        color_scraper.process()
        if color_scraper.colors:
            for color_details in color_scraper.colors:
                color_details_with_metadata = self.add_color_conversion_metadata(
                    color_details=color_details)
                color_details_with_metadata['movie'] = movie
                color_details_with_metadata['director'] = self.director
                save_row(file=self.extracted_colors_path,
                         row=color_details_with_metadata,
                         field_names=sorted(color_details_with_metadata.keys()))
        else:
            logger.error('Unable to extract features for image: ' \
                         '{film_still}'.format(film_still=film_still))

    def add_color_conversion_metadata(self, color_details=None):
        r, g, b, lab, hsv, hsl = self.get_conversions(
            color_details=color_details)
        color_details['r'] = r
        color_details['g'] = g
        color_details['b'] = b
        color_details['lab_l'] = lab.lab_l
        color_details['lab_a'] = lab.lab_a
        color_details['lab_b'] = lab.lab_b
        color_details['observer'] = lab.observer
        color_details['illuminant'] = lab.illuminant
        color_details['hsv_h'] = hsv.hsv_h
        color_details['hsv_s'] = hsv.hsv_s
        color_details['hsv_v'] = hsv.hsv_v
        color_details['hsl_h'] = hsl.hsl_h
        color_details['hsl_s'] = hsl.hsl_s
        color_details['hsl_l'] = hsl.hsl_l
        return color_details

    def get_conversions(self, color_details=None):
        r, g, b = hex_to_rgb(color_details['hex'])
        lab = lab_from_rgb((r, g, b))
        hsv = hsv_from_lab(lab)
        hsl = hsl_from_lab(lab)
        return (r, g, b, lab, hsv, hsl)

    def transform(self):
        pass

    def load(self):
        pass

if __name__ == '__main__':

    args = Arguments(description='a script to upload images to tineye labs'
                                 'and scrape extrated color information. '
                                 'You can pass a director name, '
                                 'and optionally a list of movie names. '
                                 'If no director name '
                                 'is passed, the script defaults to all directors.')

    args.add_argument(
        '--director',
        help='a single director name',
    )
    args.add_argument(
        '--movies',
        help='a list of movies associated with the director '
             '(e.g. "mulholland_drive" "blue_velvet")',
        nargs='*'
    )

    director = args.get('--director', None)
    movies = args.get('--movies', None)

    if not director:
        directors = ['wes_anderson', 'david_lynch']
    else:
        directors = [director]

    image_path = '/Users/marswilliams/wesandersone/images/'

    for director in directors:
        if not movies:
            movies = [x[1] for x in os.walk(
                '{image_path}/{director}/'.format(image_path=image_path,
                                                  director=director),
                topdown=False)][-1]
        workflow = ColorScraperWorkflow(movies=movies,
                                        director=director,)

        workflow.process()
