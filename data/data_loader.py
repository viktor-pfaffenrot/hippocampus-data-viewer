import numpy as np
import pandas as pd
import glob
import nibabel as nib
import os
import json

def load_surface_data(datpath: str):
    """
    Loads surface data into dataframe
    """

    if os.path.isfile(datpath + "/surface_data.pkl"):
        wide = pd.read_pickle(datpath + '/surface_data.pkl')
    else:
        folders = glob.glob(datpath + "/*/")

        df_list = []
        for idx, folder in enumerate(folders):
            subject = os.path.basename(folder.rstrip("/"))

            # loop over files in breath-hold dir
            BH_files = glob.glob(folder + "breathhold/*.gii")
            BH_files = [x for x in BH_files if "_stdev_" not in x]
            if BH_files:
                for BH_file in BH_files:
                    dat = nib.load(BH_file).darrays[0].data.reshape(-1, 1)
                    Overlay = BH_file.split("_", 3)[-1].split(".shape", 1)[0]
                    Layer = "inner" if "inner" in BH_file else "outer"
                    out = {
                        "Subject": subject,
                        "Layer": Layer,
                        "Overlay": Overlay,
                        "Data": dat,
                    }
                    df_list.append(out)

            # loop over files in memory dir
            mem_files = glob.glob(folder + "memory/native/*.gii")
            if (subject == "7495") | (subject == "7566"):
                mem_files = glob.glob(folder + "memory/ses-01/native/*.gii")
            elif subject == "avg":
                mem_files = glob.glob(folder + "memory/*.gii")
            mem_files = [
                x for x in mem_files if "tSNR" in x and "_stdev_" not in x
            ]
            for mem_file in mem_files:
                dat = nib.load(mem_file).darrays[0].data.reshape(-1, 1)
                Overlay = mem_file.split("_", 3)[-1].split(".shape", 1)[0]
                Layer = "inner" if "inner" in mem_file else "outer"
                out = {
                    "Subject": subject,
                    "Layer": Layer,
                    "Overlay": Overlay,
                    "Data": dat,
                }
                df_list.append(out)

            # loop over files in hippunfold dir
            if subject == "avg":
                struct_files_base = glob.glob(folder + "hippunfold/*.gii")
                struct_files = [
                    x
                    for x in struct_files_base
                    if "hemi-L" in x
                    and ".surf" in x
                    and "midthickness" not in x
                    and "atlas-bigbrain" not in x
                    and "stdev" not in x
                ]
            else:
                struct_files_base = glob.glob(folder + "hippunfold/surf/*.gii")
                struct_files = [
                    x
                    for x in struct_files_base
                    if "hemi-L" in x
                    and "label-hipp" in x
                    and "space-T2w" in x
                    and ".surf" in x
                    and "midthickness" not in x
                    and "atlas-bigbrain" not in x
                ]
            struct_files.append([x for x in struct_files_base if "atlas-bigbrain_subfields.label" in x and "hemi-L" in x][0])
            
            for struct_file in struct_files:
                if ".label" in struct_file:
                    dat = nib.load(struct_file).darrays
                    Overlay = "Labels"
                    Layer = "Canonical"
                else:   
                    dat = nib.load(struct_file).darrays[0:2]
                    if subject == "avg":
                        Overlay = struct_file.split(".", 3)[-3]
                    else:
                        Overlay = "native"
                    Layer = "inner" if "inner" in struct_file else "outer"
                    
                out = {
                    "Subject": subject,
                    "Layer": Layer,
                    "Overlay": Overlay,
                    "Data": dat,
                }
                df_list.append(out)

        df = pd.DataFrame(
            df_list, columns=["Subject", "Layer", "Overlay", "Data"]
        )
        # From long to wide format
        wide = df.pivot(
            index=["Subject", "Layer"], columns="Overlay", values="Data"
        )
        
        wide["Borders"] = None

        wide.to_pickle(datpath + '/surface_data.pkl')
    return wide


def load_depth_data(datpath: str):
    """
    Loads data as a function of cortical depth
    """
    if os.path.isfile(datpath + "/depth_data.pkl"):
        wide = pd.read_pickle(datpath + '/depth_data.pkl')
    else:
        folders = glob.glob(datpath + "/*/")
        df_list = []
        for idx, folder in enumerate(folders):
            subject = os.path.basename(folder.rstrip("/"))
            # loop over files in breath-hold dir
            BH_files = glob.glob(folder + "breathhold/*.json")
            if BH_files:
                for BH_file in BH_files:
                    with open(BH_file) as file:
                        dat = json.load(file)
                        
                    if "avg" in folder:
                        tmp = dat["T2s_submean"]
                        inp = ["T2s_submean","dS_mean_echo_submean","dS_mean_echo_weighted_submean"]
                    else:
                        tmp = dat["R2s"]
                        inp = ["R2s","dS_mean_echo","dS_mean_echo_weighted"]
                        
                    T2s = np.zeros((len(tmp), len(tmp[0])))
                    dSbreathhold = np.zeros((len(tmp), len(tmp[0])))
                    dSbreathhold_weighted = np.zeros((len(tmp), len(tmp[0])))
    
                    for depth in range(len(tmp)):
                        for subfield in range(len(tmp[0])):
                            if "avg" in folder:
                                T2s[depth, subfield] = dat[inp[0]][depth][subfield]
                            else:
                                T2s[depth, subfield] = dat[inp[0]][depth][subfield][0]                            
                            dSbreathhold[depth, subfield] = dat[inp[1]][depth][subfield]
                            dSbreathhold_weighted[depth, subfield] = dat[inp[2]][depth][subfield]
    
                    if "avg" not in folder:
                        T2s = (1 / T2s) * 1000
                        
                    out = {
                        "Subject": subject,
                        "dSbreathhold": dSbreathhold,
                        "dSbreathhold_weighted": dSbreathhold_weighted,
                        "T2s": (1 / T2s) * 1000,
                        }
    
                    df_list.append(out)
    
            # loop over files in memory dir
            mem_files = glob.glob(folder + "memory/z_transformed/*.json")
            if (subject == "7495") | (subject == "7566"):
                mem_files = glob.glob(
                    folder + "memory/ses-01/z_transformed/*.json"
                )
            elif (subject == "avg"):
                mem_files = glob.glob(folder + "memory/*.json")
            mem_files = [
                x
                for x in mem_files
                if ("memory_vs_math" or "pre_vs_post" in x) and "unfolded" not in x
            ]
            if subject != "avg":
                mem_files = [mem_files[ii] for ii in [0, 1, 4, 5]]
            for mem_file in mem_files:
                with open(mem_file) as file:
                    dat = json.load(file)
    
                vessel_masked = True if "vessel_masked" in mem_file else False
                contrast = (
                    "memory_vs_math"
                    if "memory_vs_math" in mem_file
                    else "pre_vs_post"
                )
                tmp = dat["con_array"]
                beta = np.zeros((len(tmp), len(tmp[0]))).T
                tSNR = np.zeros((len(tmp), len(tmp[0]))).T
    
                for subfield in range(len(tmp)):
                    beta[:, subfield] = dat["con_array"][subfield]
                    tSNR[:, subfield] = dat["tSNR"][subfield]
    
                out = {
                    "Subject": subject,
                    "beta": beta,
                    "tSNR": tSNR,
                    "vessel_masked": vessel_masked,
                    "contrast": contrast,
                }
    
                df_list.append(out)
        
        wide = pd.DataFrame(
            df_list, columns=[
                "Subject", 
                "dSbreathhold", 
                "dSbreathhold_weighted", 
                "T2s",
                "beta",
                "tSNR",
                "vessel_masked",
                "contrast"])
        wide["contrast"].fillna("breathhold",inplace=True)
        wide["vessel_masked"].fillna(False,inplace=True)
        wide = wide.set_index(["Subject","contrast","vessel_masked"])
        
    
        wide.to_pickle(datpath + '/depth_data.pkl')
    return wide


datpath = os.path.dirname(__file__)
surface_data = load_surface_data(datpath=datpath)
depth_data = load_depth_data(datpath=datpath)
