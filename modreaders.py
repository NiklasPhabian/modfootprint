import starepandas
import rioxarray
import pystare
import geopandas
import pandas

def read_vnp09(file_path, roi_sids):
    # Read the MOD09
    vnp09 = starepandas.io.granules.viirsl2.VNP09(file_path, nom_res='750m')
    vnp09.read_data_750m()
    vnp09.read_timestamps()

    # Getting the geolocation info for Sensor and
    vnp03_path = vnp09.guess_companion_path(prefix='VNP03')
    vnp03 = starepandas.io.granules.VNP03MOD(vnp03_path)
    vnp03.read_data()
    vnp03.read_sidecar_index()
    vnp03.read_sidecar_latlon()

    # Converting to DF and joining
    vnp09 = vnp09.to_df(xy=True)
    vnp03 = vnp03.to_df()
    vnp09 = vnp09.join(vnp03)
    vnp09.dropna(inplace=True)
    vnp09.sids = vnp09.sids.astype('int64')
    
    if vnp09.empty:
        return pandas.DataFrame()    
    
    try:
        qf1 = starepandas.io.granules.viirsl2.decode_qf1(vnp09['QF1 Surface Reflectance'])
        qf2 = starepandas.io.granules.viirsl2.decode_qf2(vnp09['QF2 Surface Reflectance'])
    except:
        print(file_path)
        raise Exception
    vnp09 = vnp09.join(qf1).join(qf2)    
    vnp09.reset_index(drop=True, inplace=True)
    

    # Subsetting
    try:
        vnp09 = starepandas.speedy_subset(vnp09, roi_sids)
    except:
        print(file_path)
        raise Exception
        
    if vnp09.empty:
        return pandas.DataFrame()

    # Adding the lower level SIDS
    vnp09['sids14'] = vnp09.to_stare_level(14, clear_to_level=True).sids
    vnp09['sids15'] = vnp09.to_stare_level(15, clear_to_level=True).sids
    vnp09['sids16'] = vnp09.to_stare_level(16, clear_to_level=True).sids
    vnp09['sids17'] = vnp09.to_stare_level(17, clear_to_level=True).sids
    vnp09['sids18'] = vnp09.to_stare_level(18, clear_to_level=True).sids

    r = 6371007.181
    vnp09['area'] = pystare.to_area(vnp09['sids']) * r ** 2 / 1000 / 1000
    vnp09['level'] = pystare.spatial_resolution(vnp09['sids'])

    # Converting types    
    vnp09 = vnp09.rename(columns={'x': 'scan_pos', 'y': 'track_pos'})
    
    pts = geopandas.points_from_xy(vnp09.lon, vnp09.lat, crs=4326)
    mod09['center_point'] = pts
    
    return vnp09


def read_mod09(file_path, roi_sids):
    # Read the MOD09
    mod09 = starepandas.io.granules.Mod09(file_path, nom_res='500m')
    mod09.read_data_500m()
    mod09.read_sidecar_index()
    mod09.read_sidecar_latlon()
    mod09.read_timestamps()
    
    # Adding the QA State flag    
    ds_name = '1km Reflectance Data State QA'
    mod09.read_dataset(ds_name, resample_factor=2)    
    mod09.decode_state(ds_name)
    
    # Getting the geolocation info for Sensor and
    mod03_path = mod09.guess_companion_path(prefix='MOD03')    
    mod03 = starepandas.io.granules.Mod03(mod03_path, nom_res='500m')
    mod03.read_data()
    
    # Converting to DF and joining
    mod09 = mod09.to_df(xy=True)
    mod03 = mod03.to_df()    
    mod09 = mod09.join(mod03)
    
    mod09.sids = mod09.sids.astype('int64')
    mod09.dropna(inplace=True)
    mod09.reset_index(inplace=True)
    
    # Subsetting
    try:
        mod09 = starepandas.speedy_subset(mod09, roi_sids)
    except:
        print('subsetting failed')
        print(file_path)
        raise Exception
        
    if mod09.empty:
        return pandas.DataFrame()
        
    # Decode modland QA bit        
    try:
        modland = starepandas.io.granules.modis.decode_qa(mod09['500m Reflectance Band Quality'])
        mod09 = mod09.join(modland)
    except:
        print('modland decode failed')
        print(file_path)
        return pandas.DataFrame()       
        
    # Adding the lower level SIDS
    mod09['sids14'] = mod09.to_stare_level(14, clear_to_level=True).sids
    mod09['sids15'] = mod09.to_stare_level(15, clear_to_level=True).sids
    mod09['sids16'] = mod09.to_stare_level(16, clear_to_level=True).sids
    mod09['sids17'] = mod09.to_stare_level(17, clear_to_level=True).sids
    mod09['sids18'] = mod09.to_stare_level(18, clear_to_level=True).sids
    
    pts = geopandas.points_from_xy(mod09.lon, mod09.lat, crs=4326)
    mod09['center_point'] = pts
    
    r = 6371007.181
    mod09['area'] = pystare.to_area(mod09['sids']) * r**2 /1000/1000
    mod09['level'] = pystare.spatial_resolution(mod09['sids'])
    
    mod09['SensorAzimuth'] = mod09['SensorAzimuth'].astype('f2')
    mod09['SensorZenith'] = mod09['SensorZenith'].astype('f2')
    mod09['SolarAzimuth'] = mod09['SolarAzimuth'].astype('f2')
    mod09['SolarZenith'] = mod09['SolarZenith'].astype('f2')

    #mod09['500m Surface Reflectance Band 1'] = mod09['500m Surface Reflectance Band 1'].astype('f2')
    #mod09['500m Surface Reflectance Band 2'] = mod09['500m Surface Reflectance Band 2'].astype('f2')
    #mod09['500m Surface Reflectance Band 3'] = mod09['500m Surface Reflectance Band 3'].astype('f2')
    #mod09['500m Surface Reflectance Band 4'] = mod09['500m Surface Reflectance Band 4'].astype('f2')
    #mod09['500m Surface Reflectance Band 5'] = mod09['500m Surface Reflectance Band 5'].astype('f2')
    #mod09['500m Surface Reflectance Band 6'] = mod09['500m Surface Reflectance Band 6'].astype('f2')
    #mod09['500m Surface Reflectance Band 7'] = mod09['500m Surface Reflectance Band 7'].astype('f2')
        
    mod09.reset_index(inplace=True, drop=True)
    mod09 = mod09.rename(columns={'x': 'scan_pos', 'y': 'track_pos'})
    return mod09


def read_mod09ga(file_path, bbox=None, sidecar_path=None):    
    mod09ga = starepandas.io.granules.Mod09GA(file_path, sidecar_path=sidecar_path)
    if sidecar_path:    
        mod09ga.nom_res='500m'
        mod09ga.read_sidecar_index()
        mod09ga.read_sidecar_latlon()
    mod09ga.read_data()
        
    mod09ga.read_dataset('state_1km_1', resample_factor=2)    
    mod09ga.read_dataset('SensorZenith_1', resample_factor=2)    
    mod09ga.decode_state('state_1km_1')    
    mod09ga.read_timestamps()        
    mod09ga = mod09ga.to_df(xy=True)        
        
    if bbox:
        x_min=bbox[0] 
        x_max=bbox[1]
        y_min=bbox[2]
        y_max=bbox[3] 
        mod09ga = mod09ga[(mod09ga.x>=x_min)& (mod09ga.x<=x_max) & (mod09ga.y>=y_min) & (mod09ga.y<=y_max)]            
    
    mod09ga = mod09ga.dropna(axis=0, how='any')
    if mod09ga.empty:
        return mod09ga
    
    modland = starepandas.io.granules.modis.decode_qa(mod09ga['QC_500m_1'])
    modland = modland.rename('modland_qa')
    mod09ga = mod09ga.join(modland)     
    
    return mod09ga


def read_mod09ga_rasterio(file_name, x, y):
    
    bands = ['sur_refl_b01_1', 
         'sur_refl_b02_1', 
         'sur_refl_b03_1',
         'sur_refl_b04_1',
         'sur_refl_b05_1',
         'sur_refl_b06_1',
         'sur_refl_b07_1', 
         'QC_500m_1', 
         'obscov_500m_1']
    data = {}
    modis_pre = rioxarray.open_rasterio(file_name, masked=True, variable=bands)#.squeeze()
    data['timestamp'] = modis_pre.GRANULEBEGINNINGDATETIME
    for band in bands:
        data[band] = modis_pre[band][0, y, x].data/10000 # Geniuses index y/x instead of x/y
    mod09ga = starepandas.STAREDataFrame([data]).sort_values('timestamp')
    mod09ga = mod09ga.astype({'sur_refl_b01_1': 'float64',
                              'sur_refl_b02_1': 'float64',
                              'sur_refl_b03_1': 'float64',
                              'sur_refl_b04_1': 'float64',
                              'sur_refl_b05_1': 'float64',
                              'sur_refl_b06_1': 'float64',
                              'sur_refl_b07_1': 'float64'})
    return mod09ga

