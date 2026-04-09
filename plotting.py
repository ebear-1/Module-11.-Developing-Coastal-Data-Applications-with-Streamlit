import matplotlib.pyplot as plt
import cmocean

PLOT_DIMS = {"freq", "dir"}

def _prepare_for_plot(spec_obj):
    """Return a 2D freq-dir spectrum suitable for wavespectra polar plotting.

    The NDBC OPeNDAP workflow often returns a single record with singleton
    dimensions like time, lat, and lon. wavespectra's polar plotting expects a
    spectrum that has only freq and dir dimensions, so we squeeze out any
    length-1 dimensions first.
    """
    squeezed = spec_obj.squeeze(drop=True)

    remaining_dims = set(getattr(squeezed, "dims", ()))
    extra_dims = remaining_dims - PLOT_DIMS
    if extra_dims:
        raise ValueError(
            "Spectrum still has extra dimensions after squeezing: "
            f"{sorted(extra_dims)}. Remaining dims are {list(getattr(squeezed, 'dims', ()))!r}."
        )
    return squeezed


def plot_directional_spectrum(spec_obj, as_period: bool = True):
    """Plot a directional spectrum on polar axes."""
    spec2d = _prepare_for_plot(spec_obj)
    cmap_spectrum = cmocean.cm.thermal
    pobj = spec2d.spec.plot(
         kind="contourf",
         normalised=False,
         as_period= True,
         logradius=False,
         radii_ticks=[5, 10, 15, 20],
         radii_labels_angle=22.5,
         cmap=cmap_spectrum,
         colorbar=True,
         cbar_kwargs={"label": r"Variance density spectrum ($m^2$/Hz/deg)"},
        )

    ax = plt.gca()
    ax.set_title("Directional wave spectrum")
    fig = plt.gcf()
    return fig
