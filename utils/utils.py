import numpy as np
import plotly.graph_objects as go
#import sys
#sys.path.append('/home/pfaffenrot/github/VPF_hippocampus_data_viewer')

#from data import surface_data



def surfdat_smooth(faces,cdata):
    cdata_smooth = cdata.astype(float)
    
    newV = np.zeros((len(cdata),1))
    
    matches = faces[:,:,np.newaxis] == np.arange(len(cdata))
    f = np.any(matches, axis=1)
    
    for idx in range(len(cdata)):
        v = np.unique(faces[np.argwhere(f[:,idx])])
        newV[idx] = np.nanmean(cdata_smooth[v])
    return newV


def create_border_coordinates(faces,vertices,cdata):
    
    u = np.unique(cdata)
    v = {}
    for ii in u:
        b = (cdata==ii).astype(float)
        b = surfdat_smooth(faces,b)
        b = b % 1
        b = np.argwhere(b>0)
        b = np.argwhere(np.all(np.isin(faces,b),axis=1))
        
        coords = np.zeros((len(b),3))
        for idx,val in enumerate(b):
            coords[idx,:] = np.mean(vertices[faces[val,:],:],axis=1)
        
        v[str(ii)] = coords
        
    scatter_plots = []
    for _,val in v.items():
        scatter_plots.append(go.Scatter3d(
                                x=val[:,0],
                                y=val[:,1],
                                z=val[:,2],
                                mode = 'markers',
                                hoverinfo='none',
                                marker = dict(
                                    color='white',
                                    size = 5)
                                ))
    return scatter_plots
        