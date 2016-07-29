#!/usr/bin/env python
''' This script tests geodesic3D.py utility function that returns the optimal path from one point to another on a 3D cost mask (e.g. brain mask). Note
    that this is a path and not an interpolation of electrodes along a path.

It takes as inputs two sample voxel coordinates representing the starting and ending points on a mask surface as well as the mask itself used to determine the path on which to traverse. It outputs the path as determined
    by graph traversal using Djikstra's algorithm.
'''

from os import path
import sys
sys.path.append(path.abspath('../../util'))

import unittest
import time

import numpy as np
import scipy.io as sio
import nibabel as nib
import matplotlib.pyplot as plt
import json

from geodesic3D import geodesic3D

__version__ = '0.0'
__author__ = 'Lohith Kini'
__email__ = 'lkini@mail.med.upenn.edu'
__copyright__ = "Copyright 2016, University of Pennsylvania"
__credits__ = ["Xavier Islam","Sandhitsu Das", "Joel Stein",
                "Kathryn Davis"]
__license__ = "MIT"
__status__ = "Development"

DATA_DIR = 'data/'

class TestGeodesicDistance(unittest.TestCase):
    """Unit test for measuring the geodesic distance between two points
        on a 3D mask.

    Tests different forms of masks (binary) and sample points on the masks.
    """

    def load_data(self):
        """returns the JSON data as a dictionary

        Takes in coordinates from 3 sample test cases saved in
            geodesic3D_examples.json file located in the same folder as this
            unit test.
        """
        with open('geodesic3D_examples.json') as data_file:
            data = json.load(data_file)
        # Set filepath to data
        global DATA_DIR
        DATA_DIR = str(data['DATA_DIR'])
        return data

    def test_patients(self,patient_id):
        """returns True or False depending on the success of creating a
            synthetic path on a 3D mask.

        @param patient_id: Sample test patient ID
        @type patient_id: string
        @rtype: bool
        """
        try:
            preprocess_start = time.clock()
            # Load the test coordinates
            data = self.load_data()

            # Load the segmentation file
            seg_filename = '%s/%s_unburied_electrode_seg.nii.gz'%(
                DATA_DIR,
                patient_id
                )
            seg = nib.load(path.expanduser(seg_filename))
            seg_data = seg.get_data()

            mask_filename = '%s/%s_brain_mask.nii.gz'%(
                DATA_DIR,
                patient_id
                )
            mask = nib.load(path.expanduser(mask_filename))
            mask_data = mask.get_data()

            # Initialize the result 3d image matrix
            res = np.zeros(seg_data.shape)

            # Set the output file name
            out_filename = seg_filename[:-35] + '%s_interpol.nii.gz'%patient_id

            # Interpolate on the 2-3 corners
            grid = data[patient_id]["1"]["grid_config"]
            M = int(grid.split('x')[0])
            N = int(grid.split('x')[1])
            radius = 0.2 * 10

            print 'Preprocessing took: %s ms'%(
                (time.clock()-preprocess_start)*1000
                )

            interpol_start = time.clock()

            traversal_path = geodesic3D(
                tuple(data[patient_id]["1"]["A"]),
                tuple(data[patient_id]["1"]["B"]),
                mask_data
                )

            print 'Interpolation took: %s s'%(
                (time.clock()-interpol_start)
                )

            nib_start = time.clock()
            # Create spheres of radius
            for point in traversal_path:
                res[point[0]-radius:point[0]+radius,
                    point[1]-radius:point[1]+radius,
                    point[2]-radius:point[2]+radius] = 1

            # Save res as new output result file
            res_nifti = nib.Nifti1Image(res,seg.get_affine())
            nib.save(res_nifti,path.expanduser(out_filename))
            print 'Postprocessing (which includes creating the final NIfTI \
                file) took: %s ms'%((time.clock()-nib_start)*1000)

            return True
        except Exception, e:
            print str(e)
            return False

    def test_geodesic3D_test_1(self):
        """Unit test for patient HUP64."""
        patient_id = 'HUP64'
        return self.test_patients(patient_id)

    def test_geodesic3D_test_2(self):
        """Unit test for patient HUP65."""
        patient_id = 'HUP65'
        return self.test_patients(patient_id)

    def test_geodesic3D_test_3(self):
        """Unit test for patient geodesic2D_test_3."""
        patient_id = 'HUP86'
        return self.test_patients(patient_id)

    def test_geodesic3D_test_4(self):
        """Unit test for patient geodesic2D_test_3."""
        patient_id = 'HUP87'
        return self.test_patients(patient_id)

    def runTest(self):
        """Required method for running a unit test."""
        return self.test_geodesic3D_test_1()


if __name__ == '__main__':
    ti = TestGeodesicDistance()
    ti.test_geodesic3D_test_1()
