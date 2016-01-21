#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Retrieves dominant colors for film stills using k-means clustering
import logging
import os
from wesandersone.utilities import command
from wesandersone.utilities.arguments import Arguments
from wesandersone.utilities.color import hex_to_rgb, hsl_from_lab, hsv_from_lab, lab_from_rgb, rgb_to_hex
from wesandersone.utilities.writer import save_row
from wesandersone.workflows.base_etl_workflow import BaseETLWorkflow
from color_cluster import ColorCluster

logger = logging.getLogger(__name__)


class ColorClusteringWorkflow(BaseETLWorkflow):

    def __init__(self,
                 movies=None,
                 director=None,
                 num_clusters=None):
        super(ColorClusteringWorkflow, self).__init__(workflow_name='color_clustering')
        self.movies = movies
        self.director = director
        self.num_clusters = num_clusters
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
        color_clusterer = ColorCluster(image=film_still, num_clusters=self.num_clusters)
        color_clusterer.process()
        for color_details in color_clusterer.dominant_colors:
            color_details_map = {}
            conversions = self.get_conversions(
            color_details=color_details)
            color_details_map_with_metadata = self.add_color_conversion_metadata(
                conversions=conversions, color_details_map=color_details_map)
            color_details_map_with_metadata['movie'] = movie
            color_details_map_with_metadata['director'] = self.director
            save_row(file=self.extracted_colors_path,
                     row=color_details_map_with_metadata,
                     field_names=sorted(color_details_map_with_metadata.keys()))

    def add_color_conversion_metadata(self, conversions=None, color_details_map=None):
        r, g, b, hex, lab, hsv, hsl = conversions
        color_details_map['r'] = r
        color_details_map['g'] = g
        color_details_map['b'] = b
        color_details_map['hex'] = hex
        color_details_map['lab_l'] = lab.lab_l
        color_details_map['lab_a'] = lab.lab_a
        color_details_map['lab_b'] = lab.lab_b
        color_details_map['observer'] = lab.observer
        color_details_map['illuminant'] = lab.illuminant
        color_details_map['hsv_h'] = hsv.hsv_h
        color_details_map['hsv_s'] = hsv.hsv_s
        color_details_map['hsv_v'] = hsv.hsv_v
        color_details_map['hsl_h'] = hsl.hsl_h
        color_details_map['hsl_s'] = hsl.hsl_s
        color_details_map['hsl_l'] = hsl.hsl_l
        return color_details_map

    def get_conversions(self, color_details=None):
        r, g, b = color_details
        hex = rgb_to_hex([r, g, b])
        lab = lab_from_rgb((r, g, b))
        hsv = hsv_from_lab(lab)
        hsl = hsl_from_lab(lab)
        return (r, g, b, hex, lab, hsv, hsl)

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
    args.add_argument(
        '--num_clusters',
        help='an integer value that '
             'represents the number of clusters',
        type=int
    )
    director = args.get('--director', None)
    movies = args.get('--movies', None)
    num_clusters = args.get('--num_clusters', 15)

    if director and not movies:
        raise Exception('You must pass a list of '
                        '--movies if you pass a --director.')

    if not director:
        directors = ['wes_anderson', 'david_lynch']
    else:
        directors = [director]

    image_path = '/Users/marswilliams/wesandersone/images/'

    for director in directors:
        movies = [x[1] for x in os.walk(
            '{image_path}/{director}/'.format(image_path=image_path,
                                              director=director),
            topdown=False)][-1]
        workflow = ColorClusteringWorkflow(movies=movies,
                                           director=director,
                                           num_clusters=num_clusters)

        workflow.process()
