"""Test for alff."""
import os
import shutil

import nibabel as nb
import numpy as np

from xcp_d.tests.utils import get_nodes
from xcp_d.utils.bids import _get_tr
from xcp_d.utils.write_save import read_ndata, write_ndata
from xcp_d.workflows import restingstate


def test_nifti_alff(fmriprep_with_freesurfer_data, tmp_path_factory):
    """Test ALFF computations as done for Niftis.

    Get the FFT of a Nifti, add to the amplitude of its lower frequencies
    and confirm the mean ALFF after addition to lower frequencies
    has increased.
    """
    # Get the file names
    bold_file = fmriprep_with_freesurfer_data["nifti_file"]
    bold_mask = fmriprep_with_freesurfer_data["brain_mask_file"]

    # Let's initialize the ALFF node
    TR = _get_tr(nb.load(bold_file))
    compute_alff_wf = restingstate.init_compute_alff_wf(
        omp_nthreads=2,
        bold_file=bold_file,
        mem_gb=4,
        TR=TR,
        lowpass=0.08,
        highpass=0.01,
        cifti=False,
        smoothing=6,
        name="compute_alff_wf",
    )

    # Let's move to a temporary directory before running
    tempdir = tmp_path_factory.mktemp("test_ALFF_nifti")
    compute_alff_wf.base_dir = tempdir
    compute_alff_wf.inputs.inputnode.bold_mask = bold_mask
    compute_alff_wf.inputs.inputnode.clean_bold = bold_file
    compute_alff_res = compute_alff_wf.run()
    nodes = get_nodes(compute_alff_res)

    # Let's get the mean of the ALFF for later comparison
    original_alff = nodes["compute_alff_wf.alff_compt"].get_output("alff_out")
    original_alff_data_mean = nb.load(original_alff).get_fdata().mean()

    # Now let's do an FFT
    original_bold_data = read_ndata(bold_file, bold_mask)

    # Let's work with a single voxel
    voxel_data = original_bold_data[2, :]
    fft_data = np.fft.fft(voxel_data)
    mean = fft_data.mean()

    # Let's increase the values of the first few frequency's amplitudes
    # to create fake data
    fft_data[:11] += 300 * mean

    # Let's convert this back into time domain
    changed_voxel_data = np.fft.ifft(fft_data)
    # Let's replace the original value with the fake data
    original_bold_data[2, :] = changed_voxel_data
    # Let's write this out
    filename = os.path.join(tempdir, "editedfile.nii.gz")
    write_ndata(original_bold_data, template=bold_file, mask=bold_mask, filename=filename)

    # Now let's compute ALFF for the new file and see how it compares
    # to the original ALFF - it should increase since we increased
    # the amplitude in low frequencies for a voxel
    tempdir = tmp_path_factory.mktemp("test_ALFF_nifti_dir2")
    compute_alff_wf.base_dir = tempdir
    compute_alff_wf.inputs.inputnode.bold_mask = bold_mask
    compute_alff_wf.inputs.inputnode.clean_bold = filename
    compute_alff_res = compute_alff_wf.run()
    nodes = get_nodes(compute_alff_res)

    # Let's get the new ALFF mean
    new_alff = nodes["compute_alff_wf.alff_compt"].get_output("alff_out")
    assert os.path.isfile(new_alff)
    new_alff_data_mean = nb.load(new_alff).get_fdata().mean()

    # Now let's make sure ALFF has increased ...
    assert new_alff_data_mean > original_alff_data_mean


def test_cifti_alff(fmriprep_with_freesurfer_data, tmp_path_factory):
    """Test ALFF computations as done for Ciftis.

    Get the FFT of a Cifti, add to the amplitude of its lower frequencies
    and confirm the ALFF after addition to lower frequencies
    has changed in the expected direction.
    """
    bold_file = fmriprep_with_freesurfer_data["cifti_file"]
    bold_mask = fmriprep_with_freesurfer_data["brain_mask_file"]

    # Let's initialize the ALFF node
    TR = _get_tr(nb.load(bold_file))
    compute_alff_wf = restingstate.init_compute_alff_wf(
        omp_nthreads=2,
        bold_file=bold_file,
        mem_gb=4,
        TR=TR,
        lowpass=0.08,
        highpass=0.01,
        cifti=True,
        smoothing=6,
    )

    # Let's move to a temporary directory before running
    tempdir = tmp_path_factory.mktemp("test_ALFF_cifti")
    compute_alff_wf.base_dir = tempdir
    compute_alff_wf.inputs.inputnode.bold_mask = bold_mask
    compute_alff_wf.inputs.inputnode.clean_bold = bold_file
    compute_alff_res = compute_alff_wf.run()
    nodes = get_nodes(compute_alff_res)

    # Let's get the mean of the data for later comparison
    original_alff = nodes["compute_alff_wf.alff_compt"].get_output("alff_out")
    original_alff_data_mean = nb.load(original_alff).get_fdata().mean()

    # Now let's do an FFT
    original_bold_data = read_ndata(bold_file, bold_mask)

    # Let's work with a single voxel
    voxel_data = original_bold_data[2, :]
    fft_data = np.fft.fft(voxel_data)
    mean = fft_data.mean()
    # Let's increase the amplitudes for the lower frequencies
    fft_data[:11] += 300 * mean
    # Let's get this back into the time domain
    changed_voxel_data = np.fft.ifft(fft_data)
    # Let's replace the original value with the fake data
    original_bold_data[2, :] = changed_voxel_data

    # Let's write this out
    filename = os.path.join(tempdir, "editedfile.dtseries.nii")
    write_ndata(original_bold_data, template=bold_file, mask=bold_mask, filename=filename)

    # Now let's compute ALFF for the new file and see how it compares
    tempdir = tmp_path_factory.mktemp("test_ALFF_cifti_dir2")
    compute_alff_wf.base_dir = tempdir
    compute_alff_wf.inputs.inputnode.bold_mask = bold_mask
    compute_alff_wf.inputs.inputnode.clean_bold = filename
    compute_alff_res = compute_alff_wf.run()
    nodes = get_nodes(compute_alff_res)

    # Let's get the new ALFF mean
    new_alff = nodes["compute_alff_wf.alff_compt"].get_output("alff_out")
    assert os.path.isfile(new_alff)
    new_alff_data_mean = nb.load(new_alff).get_fdata().mean()

    # Now let's make sure ALFF has increased, as we added
    # to the amplitude of the lower frequencies in a voxel
    assert new_alff_data_mean > original_alff_data_mean


def _add_noise(image):
    """Add Gaussian noise.

    Source: "https://stackoverflow.com/questions/22937589/" \
    "how-to-add-noise-gaussian-salt-and-pepper-etc-to-image-" \
    "in-python-with-opencv"
    """
    row, col = image.shape
    mean = 0
    var = 0.1
    sigma = var**0.5
    gauss = np.random.normal(mean, sigma, (row, col))
    gauss = gauss.reshape(row, col)
    noisy_img = image + (gauss * 200)
    return noisy_img


def test_nifti_reho(fmriprep_with_freesurfer_data, tmp_path_factory):
    """Test Nifti ReHo Computation.

    Confirm that ReHo decreases after adding noise to a
    Nifti image.
    """
    tempdir = tmp_path_factory.mktemp("test_REHO_nifti")

    # Get the names of the files
    bold_file = fmriprep_with_freesurfer_data["nifti_file"]
    bold_mask = fmriprep_with_freesurfer_data["brain_mask_file"]

    # Set up and run the ReHo wf in a tempdir
    reho_wf = restingstate.init_nifti_reho_wf(omp_nthreads=2, mem_gb=4, bold_file=bold_file)
    reho_wf.inputs.inputnode.bold_mask = bold_mask
    reho_wf.base_dir = tempdir
    reho_wf.inputs.inputnode.clean_bold = bold_file
    reho_res = reho_wf.run()
    nodes = get_nodes(reho_res)

    # Get the original mean of the ReHo for later comparison
    original_reho = nodes["nifti_reho_wf.reho_3d"].get_output("out_file")
    original_reho_mean = nb.load(original_reho).get_fdata().mean()
    original_bold_data = read_ndata(bold_file, bold_mask)

    # Add some noise to the original data and write it out
    noisy_bold_data = _add_noise(original_bold_data)
    noisy_bold_file = os.path.join(tempdir, "test.nii.gz")
    write_ndata(
        noisy_bold_data,
        template=bold_file,
        mask=bold_mask,
        filename=noisy_bold_file,
    )

    # Run ReHo again
    assert os.path.isfile(noisy_bold_file)
    reho_wf.inputs.inputnode.clean_bold = noisy_bold_file
    reho_res = reho_wf.run()
    nodes = get_nodes(reho_res)

    # Has the new ReHo's mean decreased?
    new_reho = nodes["nifti_reho_wf.reho_3d"].get_output("out_file")
    new_reho_mean = nb.load(new_reho).get_fdata().mean()
    assert new_reho_mean < original_reho_mean


def test_cifti_reho(fmriprep_with_freesurfer_data, tmp_path_factory):
    """Test Cifti ReHo Computation.

    Confirm that ReHo decreases after adding noise to a
    Cifti image.
    """
    # Get the names of the files
    tempdir = tmp_path_factory.mktemp("test_REHO_cifti")
    source_file = fmriprep_with_freesurfer_data["cifti_file"]

    # Create a copy of the BOLD file to control the filename
    orig_bold_file = os.path.join(tempdir, "original.dtseries.nii")
    shutil.copyfile(source_file, orig_bold_file)

    # Set up and run the ReHo wf in a tempdir
    reho_wf = restingstate.init_cifti_reho_wf(
        omp_nthreads=2, mem_gb=4, name="orig_reho_wf", bold_file=source_file
    )
    reho_wf.base_dir = tempdir
    reho_wf.inputs.inputnode.clean_bold = orig_bold_file
    reho_res = reho_wf.run()
    nodes = get_nodes(reho_res)

    # Get the original mean of the ReHo for later comparison
    original_reho = nodes["orig_reho_wf.merge_cifti"].get_output("out_file")
    original_reho_mean = nb.load(original_reho).get_fdata().mean()

    # Add some noise to the original data and write it out
    original_bold_data = read_ndata(orig_bold_file)
    noisy_bold_data = _add_noise(original_bold_data)
    noisy_bold_file = os.path.join(tempdir, "noisy.dtseries.nii")
    write_ndata(noisy_bold_data, template=orig_bold_file, filename=noisy_bold_file)

    # Run ReHo again
    assert os.path.isfile(noisy_bold_file)

    # Create a new workflow
    reho_wf = restingstate.init_cifti_reho_wf(
        omp_nthreads=2, mem_gb=4, name="noisy_reho_wf", bold_file=source_file
    )
    reho_wf.base_dir = tempdir
    reho_wf.inputs.inputnode.clean_bold = noisy_bold_file
    reho_res = reho_wf.run()
    nodes = get_nodes(reho_res)

    # Has the new ReHo's mean decreased?
    noisy_reho = nodes["noisy_reho_wf.merge_cifti"].get_output("out_file")
    noisy_reho_mean = nb.load(noisy_reho).get_fdata().mean()
    assert noisy_reho_mean < original_reho_mean