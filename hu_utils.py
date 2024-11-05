
import datetime

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import pydicom as dicom
from pydicom.pixel_data_handlers.util import apply_modality_lut
from pydicom.uid import ExplicitVRLittleEndian, generate_uid
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset

from utils import *

def trim_img(img, trim):
    if trim is not None:
        return img[trim[0]:trim[1], trim[2]:trim[3]]
    else:
        return img

def load_hu(path, trim):
    dcm = dicom.dcmread(path, force=True)
    pixel = dcm.pixel_array
    hu = apply_modality_lut(pixel, dcm)
    hu = trim_img(hu, trim)
    return hu

def write_decom(pixel_array, filename, series_name='Series'):
    today_date = datetime.datetime.now().strftime('%Y%m%d')
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian  # Use Explicit VR Little Endian
    file_meta.ImplementationClassUID = generate_uid()
    
    ds = Dataset()
    ds.file_meta = file_meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    
    ds.PatientName = "Test^Firstname"
    ds.PatientID = "123456"
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.FrameOfReferenceUID = generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    
    ds.Modality = 'CT'
    ds.StudyDate = today_date
    ds.SeriesDate = today_date
    ds.AcquisitionDate = today_date
    ds.SeriesDescription = series_name
    
    ds.Rows, ds.Columns = pixel_array.shape[1], pixel_array.shape[2]
    ds.NumberOfFrames = pixel_array.shape[0]
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelSpacing = [1, 1]  # Assuming 1mm x 1mm pixel spacing
    ds.SliceThickness = 1  # Assuming each slice is 1mm thick
    ds.PixelRepresentation = 1
    ds.BitsStored = 16
    ds.BitsAllocated = 16
    ds.HighBit = 15

    ds.PixelData = pixel_array.astype(np.int16).tobytes()
    
    dicom.dcmwrite(filename, ds, write_like_original=False)