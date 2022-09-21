# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""A range of utility functions for xcp_d interfaces and workflows."""
from xcp_d.utils.bids import (
    collect_data,
    collect_participants,
    extract_t1w_seg,
    select_cifti_bold,
    select_registrationfile,
)
from xcp_d.utils.concantenation import concatenatebold
from xcp_d.utils.confounds import load_confound_matrix
from xcp_d.utils.dcan2fmriprep import dcan2fmriprep
from xcp_d.utils.execsummary import (
    generate_brain_sprite,
    get_regplot,
    plot_registrationx,
    ribbon_to_statmap,
    surf2vol,
)
from xcp_d.utils.fcon import (
    compute_2d_reho,
    compute_alff,
    extract_timeseries_funct,
    mesh_adjacency,
)
from xcp_d.utils.hcp2fmriprep import hcp2fmriprep
from xcp_d.utils.modified_data import compute_fd, generate_mask, interpolate_masked_data
from xcp_d.utils.plot import (
    compute_dvars,
    confoundplot,
    plot_carpet,
    plot_svg,
    plot_svgx,
    plotimage,
)
from xcp_d.utils.qcmetrics import compute_registration_qc
from xcp_d.utils.sentry import sentry_setup
from xcp_d.utils.utils import (
    fwhm2sigma,
    get_customfile,
    get_maskfiles,
    get_transformfile,
    get_transformfilex,
    stringforparams,
)
from xcp_d.utils.write_save import (
    despikedatacifti,
    read_gii,
    read_ndata,
    write_gii,
    write_ndata,
)

__all__ = [
    'read_ndata',
    'write_ndata',
    'read_gii',
    'write_gii',
    'plot_svg',
    'compute_dvars',
    'load_confound_matrix',
    'collect_participants',
    'collect_data',
    'compute_2d_reho',
    'extract_timeseries_funct',
    'compute_alff',
    'mesh_adjacency',
    'interpolate_masked_data',
    'generate_mask',
    'compute_fd',
    'bid_derivative',
    'sentry_setup',
    'despikedatacifti',
    'compute_registration_qc',
    'get_maskfiles',
    'get_transformfile',
    'get_transformfilex',
    'stringforparams',
    'fwhm2sigma',
    'get_customfile',
    'select_registrationfile',
    'select_cifti_bold',
    'plot_svgx',
    'plot_carpet',
    'confoundplot',
    'surf2vol',
    'get_regplot',
    'plot_registrationx',
    'generate_brain_sprite',
    'plotimage',
    'extract_t1w_seg',
    'ribbon_to_statmap',
    'dcan2fmriprep',
    'hcp2fmriprep',
    'concatenatebold',
]
