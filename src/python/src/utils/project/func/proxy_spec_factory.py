from utils.containers import GeoSerf, ProxySpec, BrightDataDatacenter, BrightDataResidential


def proxy_spec_factory(proxy_type, **kwargs):
    if proxy_type.startswith("geoserf1"):
        return GeoSerf(standard_rotate_interval=1, **kwargs)
    if proxy_type.startswith("geoserf5"):
        return GeoSerf(standard_rotate_interval=5, **kwargs)
    if proxy_type.startswith("geoserf15"):
        return GeoSerf(standard_rotate_interval=15, **kwargs)
    if proxy_type.startswith("bright_data_datacenter"):
        return BrightDataDatacenter(**kwargs)
    if proxy_type.startswith("bright_data_residential"):
        return BrightDataResidential(**kwargs)
    else:
        return ProxySpec(**kwargs)
