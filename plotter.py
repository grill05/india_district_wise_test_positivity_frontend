import os, sys
import pandas as pd

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from districts_map import *

# generic option to toggle b/w linear/log scale (by adding buttons on the left of a graph)
updatemenus = [
    dict(
        type="buttons",
        direction="up",
        buttons=list(
            [
                dict(
                    args=[{"yaxis.type": "linear"}],
                    label="Linear Scale",
                    method="relayout",
                ),
                dict(
                    args=[{"yaxis.type": "log"}], label="Log Scale", method="relayout"
                ),
                dict(
                    args=[{"yaxis2.type": "linear"}],
                    label="Linear Scale2",
                    method="relayout",
                ),
                dict(
                    args=[{"yaxis2.type": "log"}], label="Log Scale2", method="relayout"
                ),
            ]
        ),
    ),
]

if __name__ == "__main__":
    # ~ # download the repo to access *csv files
    
    os.system(
        "git clone --depth 1 https://github.com/grill05/india_district_wise_test_positivity && mv india_district_wise_test_positivity/*csv . && rm -rf misc_bed_availability_scraper"
    )
    os.system(
        "git clone --depth 1 https://github.com/grill05/covid19india_data_parser && mv covid19india_data_parser/*.py . && rm -rf covid19india_data_parser"
    )
    os.system("curl -# -O https://data.covid19bharat.org/csv/latest/states.csv")
    os.system("curl -# -O https://data.covid19bharat.org/csv/latest/districts.csv")

    # logic in dataparser3.py makes it easier to access "cases" timeseries of cities/states
    import dataparser3 as dp

    
    p=pd.read_csv("india_districts_tpr.csv")
    
    # do for karnataka as test-case
    for state in state_code_to_name:
        if state in ["un"]: continue #"state unassigned" not relevant here
        
        state_name=state_code_to_name[state]        
        print('Processing state: %s' %(state_name))
        
        capital=''
        try: capital=state_capitals[state]
        except:print('Could not find capital city of '+state_name)
        
        
        ps=p[p.state==state_code_to_name[state].upper()]
        districts=list(set(list(ps.district)));districts.sort()
        
        a = open('states/'+state+'.html', "w")        
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        #add TPR of entire state, and make it visible
        try:
            dates, state_tpr = zip(*dp.get_positivity(state))
            state_tpr = pd.DataFrame({"state_tpr": state_tpr,"middle_date": pd.to_datetime([i.strftime("%Y-%m-%d") for i in dates]) })
            
            if capital:
                psd=ps[ps.district==capital]
                psd['middle_date']=pd.to_datetime(psd.week_start_date)+((pd.to_datetime(psd.week_end_date)-pd.to_datetime(psd.week_start_date))/2)
            
                state_tpr = pd.merge(psd, state_tpr, how="left")
                
            
            fig.add_trace(go.Scatter(x=state_tpr["middle_date"], y=state_tpr.state_tpr, name=state_name+' state TPR(7-day MA)', mode="lines+markers",line_shape="spline"),secondary_y=False)
        except:
            print('Could not add Statewide TPR trace for '+state_name+'!\ncontinuing with processing the districts')
        
        
        for district in districts:    
            if district in ["PRATAPGARH","BILASPUR"]: continue
                    
            # ~ print('Processing district: %s' %(district))
                        
            psd=ps[ps.district==district]
            psd['middle_date']=pd.to_datetime(psd.week_start_date)+((pd.to_datetime(psd.week_end_date)-pd.to_datetime(psd.week_start_date))/2)
            
            # ~ x2 = pd.merge(psd, state_tpr, how="left")
            
            if district==capital:
                fig.add_trace(go.Scatter(x=psd["middle_date"], y=psd.total_tpr, name=district, mode="lines+markers",line_shape="spline"),secondary_y=False)
            else:
                fig.add_trace(go.Scatter(x=psd["middle_date"], y=psd.total_tpr, name=district, mode="lines+markers",line_shape="spline",visible = "legendonly"),secondary_y=False)
            
            
         
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Weekly TPR", secondary_y=False)
        # ~ fig.update_yaxes(title_text="Bed Occupancy", secondary_y=True)
        fig.update_layout(title="Weekly District TPR in "+state_name)
       
        #save
        a.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
        
        #create fig for fraction of RT-PCR tests
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        for district in districts:    
             # ~ print('Processing district: %s' %(district))
            if district in ["PRATAPGARH","BILASPUR"]: continue
                        
            psd=ps[ps.district==district]
            psd['middle_date']=pd.to_datetime(psd.week_start_date)+((pd.to_datetime(psd.week_end_date)-pd.to_datetime(psd.week_start_date))/2)
            
            if district==capital:
                fig.add_trace(go.Scatter(x=psd["middle_date"], y=psd.fraction_of_RTPCR_tests, name=district, mode="lines+markers",line_shape="spline"),secondary_y=False)
            else:
                fig.add_trace(go.Scatter(x=psd["middle_date"], y=psd.fraction_of_RTPCR_tests, name=district, mode="lines+markers",line_shape="spline",visible = "legendonly"),secondary_y=False)
        
        fig.update_xaxes(title_text="Date")        
        fig.update_yaxes(title_text="Fraction of RT-PCR tests", secondary_y=False)
        # ~ fig.update_yaxes(title_text="Bed Occupancy", secondary_y=True)
        fig.update_layout(title="Weekly district-wise fraction of RT-PCR tests")
       
        #save
        a.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
        
        
        
        a.close()
    # ~ fig.update_layout(updatemenus=updatemenus)
    
    
 
