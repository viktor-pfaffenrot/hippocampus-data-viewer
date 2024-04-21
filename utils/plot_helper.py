import numpy as np
import pandas as pd
import matplotlib as mpl
import nibabel as nib
import plotly.graph_objects as go # type: ignore
import plotly.express as px
import unicodeit
import os

#from data.data_loader import load_surface_data,load_depth_data
from utils.utils import create_border_coordinates

"""
Python file to create function for plotting
"""

def fireice_colormap():
    fireice_path = os.path.join(os.path.dirname(__file__),"colormaps/fireice.json")
    df = pd.read_json(
       fireice_path
    )
    value = np.linspace(0, 1, df.shape[0])

    colorscale = []
    for idx, rgb in df.iterrows():
        entry = [value[idx], f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"]
        colorscale.append(entry)

    return colorscale   

def subfield_colorcode():    
     colorcode = {0: 'rgb(2, 123, 176)',
                  1: 'rgb(255, 122, 50)',
                  2: 'rgb(11, 163, 69)',
                  3: 'rgb(232, 38, 61)',
                  4: 'rgb(155, 110, 186)'
                  }
     return colorcode

def create_colormaps():
    cdict = {
        'Subfields': (subfield_colorcode(), 'subfields'), 
        'angio': (fireice_colormap(),'fireice',-10,10),
        'T2s': (mpl.cm.inferno,'inferno',0,70),
        'dSbreathhold': (fireice_colormap(),'fireice',-90,90),
        'dSbreathhold_weighted': (fireice_colormap(),'fireice',-15,15),
        'tSNR': (mpl.cm.hot, 'hot', 0, 40),
        'tSNR_vessel_masked': (mpl.cm.hot, 'hot', 0, 40),
        }

    return cdict

def create_overlay_file(
    data: dict,
    subject: str,
    Layer: str,
    Overlay: str
):
    
    gii_data = data.loc[subject,Layer][Overlay].reshape(-1, 1)

    gii = nib.gifti.GiftiImage()
    gii.add_gifti_data_array(
        nib.gifti.GiftiDataArray(
            gii_data.astype(np.float32)
        )
    )
    
    fname = f'data/sub-{subject}_{Layer}_{Overlay}.shape.gii'
    nib.save(gii, fname)

    return fname

    
Overlay_to_show = {"Subfields":"Subfields","angio":"angio [a.u.]","T2s":"T2* [ms]",
                  "dSbreathhold":"hyperemia \u0394S [a.u.]","dSbreathhold_weighted":"weighted hyperemia \u0394S [a.u.]",
                  "tSNR":"tSNR [a.u.]","tSNR_vessel_masked":"vessel masked tSNR [a.u.]","beta":"beta [a.u.]"}

colormaps = create_colormaps()
        
def create_surface_plot(surface_data, subject:str, Overlay:str, Layer:str, unfolded:bool,show_borders:bool,colorrange=None)->go.FigureWidget:
    
    #margins = dict(l=0, r=100, b=20, t=20)
    margins = dict(l=0,r=0,b=0,t=0)
    subfields = {1:"Subiculum", 2:"CA1", 3:"CA2", 4:"CA3", 5:"CA4"}
    
    
    boundaries = surface_data.loc[subject,"Canonical"]["Labels"][0].data
    calc_Borders = False
    if unfolded:
        vertices = surface_data.loc["avg","inner"]["unfolded"][1].data
        faces = surface_data.loc["avg","inner"]["unfolded"][0].data
        if surface_data.loc[("avg","Canonical"),"Borders"] is None:
            calc_Borders = True
    else:
        vertices = surface_data.loc[subject,Layer]["native"][1].data
        faces = surface_data.loc[subject,Layer]["native"][0].data
        if surface_data.loc[(subject,Layer),"Borders"] is None:
            calc_Borders = True
        
    values = surface_data.loc[subject,Layer][Overlay].reshape(-1, 1)
    
    
    #create boundaries as scatter plots. Save to dataframe if not already done to save
    #computation time
    if  calc_Borders:
        scatter_plots = create_border_coordinates(faces, vertices, boundaries)
        if unfolded:
            surface_data.at[("avg","Canonical"),"Borders"] = scatter_plots
        else:
            surface_data.at[(subject,Layer),"Borders"] = scatter_plots
        #surface_data.to_pickle(datpath + '/surface_data.pkl')
    else:
        if unfolded:
            scatter_plots = surface_data.loc["avg","Canonical"]["Borders"]
        else:
            scatter_plots = surface_data.loc[subject,Layer]["Borders"]

    #edit display when hovering over data
    customdata_values = values.flatten()
    
    if Overlay == "angio":
        customdata_values = np.where(customdata_values < 0, "vein", 
                                     np.where(customdata_values>0,"artery",0))
    
    customdata_values = customdata_values.tolist()
        
    customdata = np.stack(([subfields[val] for val in boundaries],
                           [Overlay_to_show[Overlay]]*len(values),
                           customdata_values), axis=-1)
    
    if Overlay == "angio":
        hovertemplate = "Subfield: %{customdata[0]}<br>"+\
                        "%{customdata[1]}: %{customdata[2]}<extra></extra>"
    else:
        hovertemplate = "Subfield: %{customdata[0]}<br>"+\
                        "%{customdata[1]}: %{customdata[2]:.2f}<extra></extra>"

    idx = 1 if (Overlay=="T2s" or "tSNR" in Overlay) else 0
    
    if colorrange is None:
        colorrange =[colormaps[Overlay][2],colormaps[Overlay][3]]
    #create unfolded mesh
    fig_data = [go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        intensity=values,
        opacity=1,
        colorscale=colormaps[Overlay][idx],
        cmin=colorrange[0],
        cmax=colorrange[1],
        )
    ]
    
    #add boundaries    
    if show_borders:
        fig_data.extend(scatter_plots)
    
    fig = go.FigureWidget(
        data=fig_data
        )
    
    fig.update_traces(customdata=customdata,
               hovertemplate = hovertemplate)
    
    if unfolded:
        up=dict(x=0, y=1., z=0)
        eye=dict(x=0, y=0, z=-3.5)
        center=dict(x=0, y=0, z=0)
    else:
        up=dict(x=2, y=-1, z=0)
        eye=dict(x=0, y=0, z=2.5)
        center=dict(x=0, y=0, z=0)
    
    fig.update_layout(
        dict(
            scene=dict(
                xaxis = dict(showbackground=False, visible=False),
                yaxis = dict(showbackground=False, visible=False),
                zaxis = dict(showbackground=False, visible=False)
            ),
            scene_camera=dict(
                up=up,
                eye=eye,
                center=center
            ),                
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            scene_aspectmode='data',
            margin=margins,
            showlegend=False,
            autosize=False,
            width = 1350,
            height=800,
        )
    )
    return fig


def create_line_plot(depth_data, subject, Overlay:str, contrast:str, vessel_masked:bool)->go.FigureWidget:

    vessel_masked = False if contrast == "breathhold" else vessel_masked
    labels = {"0":"Subiculum","1":"CA1","2":"CA2","3":"CA3","4":"CA4/DG"}
    
    #create a common y-axis range for all subjects
    yaxis_range = dict.fromkeys(depth_data.keys())
    yaxis_vals = [[-18,30],[-1.2,4],[20,48],[-1,2.5],[20,180]]
    
    for idx,val in enumerate(yaxis_range):
        yaxis_range[val] = yaxis_vals[idx]
    
    #create y-axis title
    if "beta" in Overlay:
        if contrast == "pre_vs_post":
            yaxis_title = (unicodeit.replace("\\beta_{pre}") +
                           unicodeit.replace("-\\beta_{post}") + " [z]")
        elif contrast == "memory_vs_math":
            yaxis_title = (unicodeit.replace("\\beta_{mem}") +
                           unicodeit.replace("-\\beta_{math}") + " [z]")
    else:
        yaxis_title = Overlay_to_show[Overlay]
    
    
    #build figure
    fig = go.FigureWidget(px.line(template='simple_white')).update_layout(yaxis_title=yaxis_title, xaxis_title=None)
    
    #store data in a 3d numpy array, 3rd dimension is subject
    for idx,s in enumerate(subject):
        if idx == 0:
            tmp = depth_data.loc[s,contrast,vessel_masked][Overlay]
            df_to_show = np.zeros(tmp.shape + (len(subject),))
            df_to_show[:,:,idx] = tmp
        else:
            df_to_show[:,:,idx]= depth_data.loc[s,contrast,vessel_masked][Overlay]
    
    
    #plot all but CA4/DG as lines
    for subfield in range(0,df_to_show.shape[1]-1):
        y = df_to_show[:,subfield,:]
        color = colormaps["Subfields"][0][subfield]
        for idx in range(len(subject)):
            
            #change opacity, width and what legend is to be shown when avg is 
            #selected
            if "avg" in subject[idx]:
                width = 5 
                opacity = 1
                showlegend = True 
            elif "avg" not in subject:
                width = 3
                opacity = 1
                showlegend = True if idx == 0 else False
            elif (idx == 0 and "avg" not in subject):
                showlegend = True
            else:
                showlegend = False
                width = 3
                opacity = 0.3
            
            #create the actual plot
            fig.add_trace(
                go.Scatter(
                x=np.arange(0,len(y)),
                y=y[:,idx],
                line=dict(
                    color=color,
                    width=width,
                    ),
                opacity=opacity,
                showlegend = showlegend,
                )
                )
    
    #plot CA4/DG as dots
    y= np.vstack([df_to_show[9,-1,:],df_to_show[29,-1,:]])
    for idx in range(len(subject)):
        
        
        #change opacity, width and what legend is to be shown when avg is 
        #selected
        if "avg" in subject[idx]:
            opacity = 1
            showlegend = True 
            text = ["DG","CA4"]
        elif "avg" not in subject:
            opacity = 1
            showlegend = True if idx == 0 else False
            text = ["DG","CA4"] if idx == 0 else None
        elif (idx == 0 and "avg" not in subject):
            showlegend = True
            text = ["DG","CA4"]
        else:
            showlegend = False
            text = None
            opacity = 0.3
        
        #create the actual plot
        fig.add_trace(
            go.Scatter(
                x=[9,29],
                y=y[:,idx],
                mode = "markers+text",
                text= text,
                textposition="middle left",
                textfont=dict(
                    size=22,
                    color='#9467BD'
                    ),
                marker=dict(
                    color='#9467BD',
                    size=18,
                    opacity=opacity
                    ),
                showlegend = showlegend,
                )
                )
            
            
    #group the lines according to subfields
    count = 0
    for idx in range(1,len(fig.data),len(subject)):
        
        subject_idx = 0
        for ii in range(idx,idx+len(subject)):

            fig.data[ii].legendgroup = labels[str(count)]
            fig.data[ii].name = labels[str(count)]
            
            if "CA4/DG" not in labels[str(count)]:
                fig.data[ii].hovertemplate = (f'subfield={labels[str(count)]}' '<br>depth=%{x}<br>' +
                                              f'{Overlay_to_show[Overlay]}: ' + '%{y:.2f}<br>' +
                                              f'Subject: {subject[subject_idx]}' +'<extra></extra>')
            else:
                fig.data[ii].hovertemplate = (f'subfield={labels[str(count)]}' '<br>' +
                                              f'{Overlay_to_show[Overlay]}: ' + '%{y:.2f}<br>' +
                                              f'Subject: {subject[subject_idx]}' +'<extra></extra>')
            subject_idx += 1
            
        count += 1    

    #seperate SRLM from the rest
    fig.add_vline(x=9, line_width=4, line_color="Black",opacity=1)


    #style layout
    fig.update_layout(
        dict(
            legend=dict(
                title="subfields"
                ),
            font=dict(
                size=22),
        xaxis = dict(
                tickmode = 'array',
                tickvals = [4,9,20,29],
                ticktext = ["SRLM","Inner","GM","Outer"],
                range = [0,30] 
                ),
        yaxis = dict(
                range=yaxis_range[Overlay]
        ),
        )
    ) 
    return fig



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
