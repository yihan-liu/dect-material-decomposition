import numpy as np
import simpleITK as sitk

def register_bspline(fixed, moving):
    fixed_img = sitk.GetImageFromArray(fixed.astype(np.float32))
    moving_img = sitk.GetImageFromArray(moving.astype(np.float32))
    
    reg_method = sitk.ImageRegistrationMethod()                 # initialize image registration method
    reg_method.SetMetricAsCorrelation()                         # similarity metric
    reg_method.SetInterpolator(sitk.sitkLinear)                 # interpolator
    
    transform_bspline = sitk.BSplineTransformInitializer(fixed_img,
                                                         [10, 10],  # Grid size of the B-spline control points
                                                         order=3)   # B-spline order
    reg_method.SetInitialTransform(transform_bspline)
    reg_method.SetOptimizerAsLBFGSB(gradientConvergenceTolerance=1e-5,
                                    numberOfIterations=500,
                                    maximumNumberOfCorrections=5)
    
    final_transform = reg_method.Execute(fixed_img, moving_img) # execute the registration
    moving_resampled = sitk.Resample(moving_img, fixed_img,
                                     final_transform,
                                     sitk.sitkLinear,
                                     0.0,
                                     moving_img.GetPixelID())   # apply transform to moving image
    
    fixed_img = sitk.Bilateral(fixed_img, domainSigma=1.0, rangeSigma=20.0, numberOfRangeGaussianSamples=100)
    moving_resampled = sitk.Bilateral(moving_resampled, domainSigma=1.0, rangeSigma=20.0, numberOfRangeGaussianSamples=100)
    
    return sitk.GetArrayFromImage(fixed_img), sitk.GetArrayFromImage(moving_resampled), final_transform