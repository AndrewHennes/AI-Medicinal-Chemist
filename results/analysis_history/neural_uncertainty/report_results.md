# Neural uncertainty benchmark

| method | measurements | calibration | r2 | rho | nll | coverage_95 | width_95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| attentive_ensemble | 1 | calibrated | 0.100 | 0.262 | 1.022 | 0.931 | 2.583 |
| attentive_ensemble | 10 | calibrated | 0.507 | 0.262 | 0.697 | 0.942 | 1.966 |
| attentive_ensemble | 1 | raw | 0.100 | 0.262 | 1.015 | 0.917 | 2.376 |
| attentive_ensemble | 10 | raw | 0.507 | 0.262 | 0.688 | 0.930 | 1.806 |
| attentive_np | 1 | calibrated | 0.076 | 0.254 | 1.052 | 0.932 | 2.669 |
| attentive_np | 10 | calibrated | 0.497 | 0.255 | 0.741 | 0.940 | 2.014 |
| attentive_np | 1 | raw | 0.076 | 0.254 | 1.057 | 0.906 | 2.324 |
| attentive_np | 10 | raw | 0.497 | 0.255 | 0.759 | 0.915 | 1.759 |
| bayesian_nn | 1 | calibrated | 0.085 | 0.270 | 1.049 | 0.918 | 2.512 |
| bayesian_nn | 10 | calibrated | 0.407 | 0.270 | 0.814 | 0.933 | 2.103 |
| bayesian_nn | 1 | raw | 0.085 | 0.270 | 1.075 | 0.896 | 2.274 |
| bayesian_nn | 10 | raw | 0.407 | 0.270 | 0.834 | 0.914 | 1.904 |
| deep_ensemble | 1 | calibrated | 0.101 | 0.276 | 1.036 | 0.918 | 2.471 |
| deep_ensemble | 10 | calibrated | 0.417 | 0.276 | 0.796 | 0.941 | 2.177 |
| deep_ensemble | 1 | raw | 0.101 | 0.276 | 1.027 | 0.910 | 2.349 |
| deep_ensemble | 10 | raw | 0.417 | 0.276 | 0.786 | 0.935 | 2.071 |
| evidential_nig | 1 | calibrated | 0.080 | 0.264 | 1.028 | 0.941 | 3.006 |
| evidential_nig | 10 | calibrated | 0.411 | 0.262 | 0.797 | 0.941 | 2.377 |
| evidential_nig | 1 | raw | 0.080 | 0.264 | 1.026 | 0.938 | 2.908 |
| evidential_nig | 10 | raw | 0.411 | 0.262 | 0.800 | 0.937 | 2.303 |
| fnn | 1 | point_only | 0.037 | 0.216 | nan | nan | nan |
| fnn | 10 | point_only | 0.037 | 0.216 | nan | nan | nan |
| fnn_anchor | 1 | point_only | 0.037 | 0.216 | nan | nan | nan |
| fnn_anchor | 10 | point_only | 0.453 | 0.218 | nan | nan | nan |
| gaussian_nn | 1 | calibrated | 0.085 | 0.266 | 1.064 | 0.921 | 2.545 |
| gaussian_nn | 10 | calibrated | 0.391 | 0.265 | 0.856 | 0.937 | 2.198 |
| gaussian_nn | 1 | raw | 0.085 | 0.266 | 1.077 | 0.902 | 2.305 |
| gaussian_nn | 10 | raw | 0.391 | 0.265 | 0.874 | 0.921 | 1.996 |
| gp_neural_mean | 1 | calibrated | 0.027 | 0.237 | 1.066 | 0.938 | 2.830 |
| gp_neural_mean | 10 | calibrated | 0.572 | 0.401 | 0.621 | 0.941 | 1.834 |
| gp_neural_mean | 1 | raw | 0.027 | 0.237 | 1.093 | 0.896 | 2.248 |
| gp_neural_mean | 10 | raw | 0.572 | 0.401 | 0.659 | 0.902 | 1.458 |
| metric_ensemble | 1 | calibrated | 0.090 | 0.255 | 1.029 | 0.927 | 2.589 |
| metric_ensemble | 10 | calibrated | 0.522 | 0.336 | 0.668 | 0.932 | 1.799 |
| metric_ensemble | 1 | raw | 0.090 | 0.255 | 1.017 | 0.917 | 2.443 |
| metric_ensemble | 10 | raw | 0.522 | 0.336 | 0.659 | 0.923 | 1.696 |
| metric_np | 1 | calibrated | 0.065 | 0.244 | 1.063 | 0.929 | 2.654 |
| metric_np | 10 | calibrated | 0.512 | 0.327 | 0.709 | 0.930 | 1.837 |
| metric_np | 1 | raw | 0.065 | 0.244 | 1.063 | 0.908 | 2.384 |
| metric_np | 10 | raw | 0.512 | 0.327 | 0.725 | 0.908 | 1.653 |
| previous_delta | 1 | point_only | -0.033 | 0.217 | nan | nan | nan |
| previous_delta | 10 | point_only | -0.033 | 0.217 | nan | nan | nan |
| previous_delta_anchor | 1 | point_only | -0.033 | 0.217 | nan | nan | nan |
| previous_delta_anchor | 10 | point_only | 0.416 | 0.221 | nan | nan | nan |


See protocol.json for locked design and the PDF for endpoint results and limitations.
