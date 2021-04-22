# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 09:32:36 2021

@author: qgump
"""
                #SECTION 1 INITIALIZION
import pandas as pd
import time
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
from matplotlib.ticker import MaxNLocator
import seaborn as sb

import PySimpleGUI as sg
from sys import exit


seasons=['winter','spring','summer','fall']
anime_types=['TV (New)','TV (Continuing)','Special','OVA','ONA','Movie']
plot_list=['Production seasons','Production years','Studio production','Studios quantity','Source repartition','Score distribution','TV (New) length','TV (Continuing) length']

style.use('ggplot')
sg.theme('DefaultNoMoreNagging') 

font='xx-large'
lgd_position='center right'
adjust={'bottom':0.11,'right':0.82,'wspace':0.35}
enlarge_fig=(18,10)
contrast_colors=['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9', '#ffffff', '#000000']
long_contrast_colors=["#000000", "#FFFF00", "#1CE6FF", "#FF34FF", "#FF4A46", "#008941", "#006FA6", "#A30059",
"#FFDBE5", "#7A4900", "#0000A6", "#63FFAC", "#B79762", "#004D43", "#8FB0FF", "#997D87",
"#5A0007", "#809693", "#FEFFE6", "#1B4400", "#4FC601", "#3B5DFF", "#4A3B53", "#FF2F80",
"#61615A", "#BA0900", "#6B7900", "#00C2A0", "#FFAA92", "#FF90C9", "#B903AA", "#D16100",
"#DDEFFF", "#000035", "#7B4F4B", "#A1C299", "#300018", "#0AA6D8", "#013349", "#00846F",
"#372101", "#FFB500", "#C2FFED", "#A079BF", "#CC0744", "#C0B9B2", "#C2FF99", "#001E09",
"#00489C", "#6F0062", "#0CBD66", "#EEC3FF", "#456D75", "#B77B68", "#7A87A1", "#788D66",
"#885578", "#FAD09F", "#FF8A9A", "#D157A0", "#BEC459", "#456648", "#0086ED", "#886F4C",
"#34362D", "#B4A8BD", "#00A6AA", "#452C2C", "#636375", "#A3C8C9", "#FF913F", "#938A81",
"#575329", "#00FECF", "#B05B6F", "#8CD0FF", "#3B9700", "#04F757", "#C8A1A1", "#1E6E00",
"#7900D7", "#A77500", "#6367A9", "#A05837", "#6B002C", "#772600", "#D790FF", "#9B9700",
"#549E79", "#FFF69F", "#201625", "#72418F", "#BC23FF", "#99ADC0", "#3A2465", "#922329",
"#5B4534", "#FDE8DC", "#404E55", "#0089A3", "#CB7E98", "#A4E804", "#324E72", "#6A3A4C"]

                #SECTION 2 FUNCTIONS DEFINITION
def stackbarcolor(df_plot,cat_list,ax,plot_name,colors_list,cat_key,tosum_key,ylabel_name,max_year,min_year,ymax=1):
    df_plot['bottom']=0    
    
    for cat_value,color in zip(cat_list,colors_list): #I want to attribute a color for each source that will be consistent for each type of anime
            print('implementing '+cat_value)
            df_cat=df_plot[df_plot[cat_key]==cat_value] #reducing the the source
            df_cat.reset_index(drop=True, inplace=True)
                                  
            ax.bar(df_cat['release-year'],df_cat[tosum_key],label=cat_value,bottom=df_cat['bottom'],color=color,edgecolor='black')
            
            #sum percent at bottom for each year/anime-type configuration so the graph become stacked                
            for year in df_cat['release-year']:
                df_plot.loc[df_plot['release-year']==year,['bottom']]=df_cat.loc[df_cat['release-year']==year,[tosum_key]].values+df_cat.loc[df_cat['release-year']==year,['bottom']].values 
                
    ax.set_ylabel(ylabel_name,fontsize=font)
    ax.xaxis.label.set_size(font)
    ax.set_title(plot_name,fontsize=font)
    ax.axis(xmax=df_plot['release-year'].max()+1,xmin=df_plot['release-year'].min()-1)
    ax.tick_params('x',labelrotation=45, labelsize=font)
    ax.tick_params('y', labelsize=font)
    ax.set(xlim=(min_year-1,max_year+1))
    ax.ticklabel_format(axis='x', style='plain', useOffset=False) #If I don't do this plt want to put the label to engineering notation
    ax.xaxis.set_major_locator(MaxNLocator(integer=True,nbins=7,prune='both')) #give instruction how to handle the tick label: integer, nb of label, remove egde label
            
    ymax=max(df_plot['bottom'].max(),ymax) #after each season I retrieve the maximum value to limit plot axis
    
    return ymax

def signature(fig):
    fig.text(0,0.005,' Data collected with MALscraPy & Plot made with MyAnalizer | Scripts available at http://github.com/Gumpy-Q',fontsize=font, backgroundcolor='grey',style='italic',color='white')

def production_season(df,min_year,max_year,anitypes,color_list): #To vizualize the sum of anime product each year for each season
    
    season_analyze=df.value_counts(['release-year','release-season','type']).reset_index(name='count') #count occurence and build the dataframe with a new column 'count'

    select_years=season_analyze[(season_analyze['release-year']<=max_year) & (season_analyze['release-year']>=min_year)] #remove years out of study scope
    select_years=select_years[select_years['type'].isin(anitypes)]
    
    contrast_colors=color_list[0:len(anitypes)+1]
    
    custom_patches=[]

    fig, axes = plt.subplots(2,2,figsize=enlarge_fig) #building a subplot for the 4 seasons
    axes = axes.flatten()
    
    ymax=0
    
    #avoid colors mismatch when getting legend
    for color in contrast_colors:
        custom_patches.append(Patch(facecolor=color, edgecolor='b')) 
    
    print('------------ plotting evolution of production by season ------------')
    
    for season,ax in zip(seasons,axes): #Season and plot goes together so I zip them
        df_season=select_years[select_years['release-season']==season].sort_values('release-year') #reducing the DataFrame to the season studied

        print('--------------'+season)
        
        ymax=stackbarcolor(df_season,anitypes,ax,season,contrast_colors,'type','count','Count',max_year,min_year,ymax)
        
    for ax in axes:
        ax.axis(ymax=ymax+5) #And then I set the limit
        ax.ticklabel_format(axis='x', style='plain', useOffset=False)
    
    signature(fig)
    fig.suptitle('Evolution of the production',fontsize=font)
    fig.legend(custom_patches, anitypes, loc=lgd_position,fontsize=font)
    
    fig.tight_layout()    
    fig.subplots_adjust(right=adjust['right'],bottom=adjust['bottom'],wspace=adjust['wspace'])
       
    fig.savefig(savepath+'/season_evolution-'+str(start_year)+'-'+str(end_year))
    fig.show()
    return fig

def production_year(df,min_year,max_year,anitypes,color_list): #To vizualize the sum of anime product each year for each season
    
    season_analyze=df.value_counts(['release-year','type']).reset_index(name='count') #count occurence and build the dataframe with a new column 'count'

    select_years=season_analyze[(season_analyze['release-year']<=max_year) & (season_analyze['release-year']>=min_year)] #remove years out of study scope
    select_years=select_years[select_years['type'].isin(anitypes)]
    
    contrast_colors=color_list[0:len(anitypes)+1]  
    custom_patches=[]    
    #avoid colors mismatch when getting legend
    for color in contrast_colors:
        custom_patches.append(Patch(facecolor=color, edgecolor='b'))
    
    print('------------ plotting evolution of production by year ------------')    
    
    fig, ax = plt.subplots(1,figsize=enlarge_fig) #building a subplot for the 4 seasons
    
    ymax=0
     
    df_year=select_years.sort_values('release-year') #reducing the DataFrame to the season studied
        
    ymax=stackbarcolor(df_year,anitypes,ax,'',contrast_colors,'type','count','Number of anime aired',max_year,min_year,ymax)
        
    ax.axis(ymax=ymax+5) #And then I set the limit
    
    signature(fig)
    fig.suptitle('Evolution of the production',fontsize=font)
    fig.legend(custom_patches, anitypes, loc=lgd_position,fontsize=font)

    fig.tight_layout()    
    fig.subplots_adjust(right=adjust['right'],bottom=adjust['bottom'])
       
    fig.savefig(savepath+'/year_evolution'+str(start_year)+'-'+str(end_year))
    fig.show()

    return fig

def source(df,min_year,max_year,anitypes,color_list,thresold=0): 
        
    select_years=df[(df['release-year']<=max_year) & (df['release-year']>=min_year)] #remove years out of study scope
    select_years=select_years[select_years['type'].isin(anitypes)] 
    
    select_years.loc[select_years['source-material'] == '-', 'source-material'] = "Unknown in MAL" #replace the default value when source is not assigned to an anime
    
    select_years=select_years.value_counts(['release-year','type','source-material']).reset_index(name='count') #transform the long list to a count for each config
    
    #getting the sum and repartition for each release-year/type couple
    select_sum=select_years.groupby(['release-year','type'])['count'].sum().reset_index(name='sum')
    select_years=pd.merge(select_years,select_sum,on=('release-year','type')) 
    select_years['percent']=select_years['count']/select_years['sum']
    
    
    select_years.loc[select_years['percent']<(thresold/100),'source-material']='Other'
    select_years=select_years.groupby(['release-year','type','source-material'])['percent'].sum().reset_index(name='percent')
    
    
    #build a descending list by percent of source material
    sources=select_years.sort_values('percent',ascending=False)['source-material'].unique()    
       
    contrast_colors=color_list[0:len(sources)]
     
    custom_patches=[]
    
    #avoid colors mismatch when getting legend
    for color in contrast_colors:
        custom_patches.append(Patch(facecolor=color, edgecolor='b')) 
    
    print('------------ plotting evolution of source material ------------')    
                
    if len(anitypes)>1:
        
        if len(anitypes)>4:
            fig, axes = plt.subplots(2,3,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
        elif len(anitypes)==2:
            fig, axes = plt.subplots(1,2,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
        else:
            fig, axes = plt.subplots(2,2,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
            
        for anime_type,ax in zip(anitypes,axes): #Season and plot goes together so I zip them
            df_type=select_years[select_years['type']==anime_type].sort_values('release-year') #reducing the DataFrame to the season studied I need the year to be at the right order for the stacking
            print('--------------'+anime_type)
            
            stackbarcolor(df_type,sources,ax,anime_type,contrast_colors,'source-material','percent','Part of the diffusion',max_year,min_year)
            for ax in axes:
                ax.set(ylim=(0,1))
                ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0, symbol='%', is_latex=False))
                
    else:
        fig, ax = plt.subplots(1,1,figsize=enlarge_fig) #building a subplot for the one choosen
        df_type=select_years.sort_values('release-year') #reducing the DataFrame to the season studied I need the year to be at the right order for the stacking
        anime_type=anitypes[0]
        print('--------------'+anime_type)
          
        stackbarcolor(df_type,sources,ax,anime_type,contrast_colors,'source-material','percent','Part of the diffusion',max_year,min_year)
        ax.set(ylim=(0,1))
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0, symbol='%', is_latex=False))

    fig.legend(custom_patches, sources, loc=lgd_position,fontsize=font)
    signature(fig)
    fig.suptitle('Source of the adaptation (if less than '+str(thresold)+'% -> Other)',fontsize=font)          
   
    fig.tight_layout()    
    fig.subplots_adjust(right=adjust['right'],bottom=adjust['bottom'],wspace=adjust['wspace'])
       
    fig.savefig(savepath+'/source-'+str(start_year)+'-'+str(end_year))
    fig.show()
    
    return fig

def production_studio(df,min_year,max_year,anitypes,color_list): 
        
    select_years=df[(df['release-year']<=max_year) & (df['release-year']>=min_year)] #remove years out of study scope
    select_years=select_years[select_years['type'].isin(anitypes)] 
    
    select_years=select_years[select_years['studio'] != '          -' ]
    select_years=select_years[select_years['studio'] != '-']
    
    select_years=select_years.value_counts(['release-year','type','studio']).reset_index(name='count') #transform the long list to a count for each config
    
    print('Selecting studios, please wait this is a long task')
    
    studios=[]
    for year in select_years['release-year']:
        for anitype in anitypes:
            studio_list=select_years[(select_years['release-year']==year) & (select_years['type']==anitype)].sort_values('count',ascending=False)['studio'].head(3).values.tolist() #building the top 3 lists for each year and anime type
            for studio in studio_list:
                studios.append(studio)              
        
    studios = list(dict.fromkeys(studios))   #tricks to remove duplicate from a list
    contrast_colors=color_list[0:len(studios)]
     
    custom_patches=[]
    
    #avoid colors mismatch when getting legend
    for color in contrast_colors:
        custom_patches.append(Patch(facecolor=color, edgecolor='b')) 
    
    print('------------ plotting evolution of studio production ------------')    
               
    if len(anitypes)>1:
        
        if len(anitypes)>4:
            fig, axes = plt.subplots(2,3,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
        elif len(anitypes)==2:
            fig, axes = plt.subplots(1,2,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
        else:
            fig, axes = plt.subplots(2,2,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
            
        for anime_type,ax in zip(anitypes,axes): #Season and plot goes together so I zip them
            df_type=select_years[select_years['type']==anime_type].sort_values('release-year') #reducing the DataFrame to the season studied I need the year to be at the right order for the stacking
            print('--------------'+anime_type)
            
            ymax=stackbarcolor(df_type,studios,ax,anime_type,contrast_colors,'studio','count','Anime produced by',max_year,min_year)
            ax.axis(ymax=ymax+5) #And then I set the limit
            ax.ticklabel_format(axis='x', style='plain', useOffset=False)         
                
    else:
        fig, ax = plt.subplots(1,1,figsize=enlarge_fig) #building a subplot for the one choosen
        df_type=select_years.sort_values('release-year') #reducing the DataFrame to the season studied I need the year to be at the right order for the stacking
        anime_type=anitypes[0]
        print('--------------'+anime_type)
          
        ymax=stackbarcolor(df_type,studios,ax,anime_type,contrast_colors,'studio','count','Anime produced by',max_year,min_year)
        ax.axis(ymax=ymax+5) #And then I set the limit
        ax.ticklabel_format(axis='x', style='plain', useOffset=False)
        

    fig.legend(custom_patches, studios, loc=lgd_position,fontsize=font)
    signature(fig)
    fig.suptitle('Evolution of the production of the top 3 studios of each year and anime type',fontsize=font)          
   
    fig.tight_layout()    
    fig.subplots_adjust(right=adjust['right']-0.1,bottom=adjust['bottom'],wspace=adjust['wspace'])
       
    fig.savefig(savepath+'/studio-'+str(start_year)+'-'+str(end_year))
    fig.show()
    
    return fig

def studio_quantity(df,min_year,max_year,anitypes,color_list): #To vizualize the sum of anime product each year for each season
    
    select_years=df[(df['release-year']<=max_year) & (df['release-year']>=min_year)] #remove years out of study scope
    select_years=select_years[select_years['type'].isin(anitypes)]
    

    select_years=select_years[select_years['studio'] != '          -' ]
    select_years=select_years[select_years['studio'] != '-']
    
    select_years=select_years[['release-year','type','studio']]
    
    select_years=select_years.drop_duplicates()
    select_years=select_years.value_counts(['release-year','type']).reset_index(name='sum')    
    
    contrast_colors=color_list[0:len(anitypes)+1]
    
    custom_patches=[]
   
    ymax=0
    
    #avoid colors mismatch when getting legend
    for color in contrast_colors:
        custom_patches.append(Patch(facecolor=color, edgecolor='b')) 
    
    print('------------ plotting evolution of studio quantity ------------')    
               
    if len(anitypes)>1:
        
        if len(anitypes)>4:
            fig, axes = plt.subplots(2,3,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
        elif len(anitypes)==2:
            fig, axes = plt.subplots(1,2,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
        else:
            fig, axes = plt.subplots(2,2,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
            
        for anime_type,ax in zip(anitypes,axes): #Season and plot goes together so I zip them
            df_type=select_years[select_years['type']==anime_type].sort_values('release-year') #reducing the DataFrame to the season studied I need the year to be at the right order for the stacking
            print('--------------'+anime_type)
            
            ymax=stackbarcolor(df_type,[anime_type],ax,anime_type,contrast_colors,'type','sum','Number of studios',max_year,min_year)
            ax.axis(ymax=ymax+5) #And then I set the limit
            ax.ticklabel_format(axis='x', style='plain', useOffset=False)         
                
    else:
        fig, ax = plt.subplots(1,1,figsize=enlarge_fig) #building a subplot for the one choosen
        df_type=select_years.sort_values('release-year') #reducing the DataFrame to the season studied I need the year to be at the right order for the stacking
        anime_type=anitypes[0]
        print('--------------'+anime_type)
          
        ymax=stackbarcolor(df_type,[anime_type],ax,anime_type,contrast_colors,'type','sum','Number of studios',max_year,min_year)
        ax.axis(ymax=ymax+5) #And then I set the limit
        ax.ticklabel_format(axis='x', style='plain', useOffset=False)

    signature(fig)
    fig.suptitle('Number of studios credited on at least one anime (cooperations are accounted as a different studio)',fontsize=font) 
    
    fig.tight_layout()    
    fig.subplots_adjust(bottom=adjust['bottom'])
       
    fig.savefig(savepath+'/studio_quantity-'+str(start_year)+'-'+str(end_year))
    fig.show()
    return fig

def episode(df,min_year,max_year,anitype,max_shown): #This function is showing the repartition of anime'lenght in the year
    select_year=df[(df['type']==anitype) & (df['episodes']>0) & (df['release-year']>=min_year) & (df['release-year']<=max_year)] #Limit my dataframe
    
    print('------------ plotting evolution of anime length ------------')
    
    fig, ax =plt.subplots(figsize=enlarge_fig)
    ax=sb.violinplot(x='release-year',y='episodes',data=select_year,bw=0.1,cut=0, scale='width',width=0.7,inner='stick',orientation='h') 
    ax.tick_params('x',labelrotation=45, labelsize=font)
    ax.tick_params('y', labelsize=font)
    ax.set_ylabel('Number of episodes per anime',fontsize=font)
    ax.set_xlabel('Diffusion year',fontsize=font)
    ax.xaxis.label.set_size(font)
    ax.set(ylim=(0,max_shown))
    ax.set_title('Repartion of anime length : '+ anitype,fontsize=font)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True,nbins=12,prune='both')) #
    
    signature(fig)
    
    fig.tight_layout()    
    fig.subplots_adjust(bottom=adjust['bottom']+0.03)
    
    fig.savefig(savepath+'/episode_'+anitype+'-'+str(start_year)+'-'+str(end_year))
    fig.show()
    
    return fig  

def score_repartition(df,min_year,max_year,anitypes): #This function is showing the repartition of anime'lenght in the year
    
    select_years=df[(df['score']>0) & (df['release-year']>=min_year) & (df['release-year']<=max_year)] #Limit my dataframe
    select_years=select_years[select_years['type'].isin(anitypes)]
    
    print('------------ plotting evolution score ------------')
    
    if len(anitypes)>1:
        
        if len(anitypes)>4:
            fig, axes = plt.subplots(2,3,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
        elif len(anitypes)==2:
            fig, axes = plt.subplots(1,2,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
        else:
            fig, axes = plt.subplots(2,2,figsize=enlarge_fig) #building a subplot for the 6 anime types
            axes = axes.flatten()
            
        for anime_type,ax in zip(anitypes,axes): #Season and plot goes together so I zip them
            df_type=select_years[select_years['type']==anime_type] #reducing the DataFrame to the season studied I need the year to be at the right order for the stacking
            print('--------------'+anime_type)
            sb.violinplot(ax=ax,x='release-year',y='score',data=df_type,bw=0.1,cut=0, scale='width',width=0.7,inner='quartile',orientation='h')

        for anime_type,ax in zip(anitypes,axes):
            ax.tick_params('x',labelrotation=45, labelsize=font)
            ax.tick_params('y', labelsize=font)
            ax.set_ylabel('Score',fontsize=font)
            ax.set_xlabel('Diffusion year',fontsize=font)
            ax.xaxis.label.set_size(font)
            ax.set(ylim=(0,10))
            ax.set_title(anime_type,fontsize=font)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True,nbins=12,prune='both'))
    
    else:
        fig, ax = plt.subplots(1,1,figsize=enlarge_fig) #building a subplot for the one choosen
        df_type=select_years.sort_values('release-year') #reducing the DataFrame to the season studied I need the year to be at the right order for the stacking
        anime_type=anitypes[0]
        print('--------------'+anime_type)

        ax=sb.violinplot(x='release-year',y='score',data=df_type,bw=0.1,cut=0, scale='width',width=0.7,inner='quartile',orientation='h') 
        ax.tick_params('x',labelrotation=45, labelsize=font)
        ax.tick_params('y', labelsize=font)
        ax.set_ylabel('Score',fontsize=font)
        ax.set_xlabel('Diffusion year',fontsize=font)
        ax.xaxis.label.set_size(font)
        ax.set(ylim=(0,10))
        ax.set_title(anime_type,fontsize=font)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True,nbins=12,prune='both')) 
    
    signature(fig)
    fig.suptitle('Score distribution',fontsize=font) 

    
    fig.tight_layout()    
    fig.subplots_adjust(bottom=adjust['bottom']+0.03)
    
    fig.savefig(savepath+'/score_'+'-'+str(start_year)+'-'+str(end_year))
    fig.show()
    
    return fig

                #SECTION 3 CHOICE
#Choosing the csv file
datavalid=False
while datavalid==False:
    layout = [[sg.Text('Path of the csv file')],
            [sg.Input(default_text='Data/MAL-all-from-winter1970-to-present.csv'), sg.FileBrowse(file_types=(("csv Files", "*.csv"),))], 
            [sg.OK(), sg.Cancel()]] 
    window = sg.Window('Get path', layout)
    event, values = window.read()
    window.close()
    if event==sg.WIN_CLOSED or event=='Cancel':
        exit()  

    path=values[0]
    window.close()
    try:
        raw=pd.read_csv(path)
        datavalid=True
    except:
        sg.popup('Could not read file.')    

raw=pd.read_csv(path)

raw['release-year']=raw['release-year'].astype(int) #I make sure they are integer as sometime it's interpreted as float
raw['episodes']=raw['episodes'].astype(int)

first_year=raw['release-year'].min()
last_year=raw['release-year'].max()

again=['Yes']
while again[0]=='Yes':
                        
    #Choosing the years to view in plot
    datavalid=False
    while datavalid==False:
        layout = [[sg.Text('Which years do you want to view ? ')],
                [sg.Text('Must be YYYY in range ['+str(first_year)+';'+str(time.localtime().tm_year+1)+']')],
                [sg.Text('From'),sg.Spin([i for i in range(first_year,time.localtime().tm_year+2)], initial_value=first_year),sg.Text('until'),sg.Spin([i for i in range(first_year,time.localtime().tm_year+2)], initial_value=last_year)], 
                [sg.OK(), sg.Cancel()]] 
        window = sg.Window('Interval selection', layout)
        event, values = window.read()
        window.close()
        
        if event==sg.WIN_CLOSED or event=='Cancel':
             exit()    
    
        start_year=values[0]
        end_year=values[1]
        try:
            start_year=int(start_year) #check if input is integer without breaking
            end_year=int(end_year)
            if start_year<1917 or start_year>time.localtime().tm_year or end_year<1917 or end_year>time.localtime().tm_year:
                sg.popup('Invalid input. Must be YYYY in range ['+str(first_year)+';'+str(time.localtime().tm_year+1)+']')
            elif start_year>end_year:
                sg.popup('Start year is after end year')
            else:
                datavalid=True
        except:
            sg.popup('Invalid input. Must be YYYY in range ['+str(first_year)+';'+str(time.localtime().tm_year+1)+']')
            
    #Choosing the type to view in plot
    type_to_viz=[]
    datavalid=False
    while datavalid==False:
        layout = [[sg.Text('Which type of content do you want to visualize ? ')],
                [[sg.CBox(anitype, default=True) for anitype in anime_types]], 
                [sg.OK(), sg.Cancel()]]
        window = sg.Window('Choosing anime type', layout)
        event, values = window.read()
        window.close()
        
        if event==sg.WIN_CLOSED or event=='Cancel':
             exit()
        
        for i in range(len(values)):
            if values[i]==True:
                type_to_viz.append(anime_types[i])
        
        if len(type_to_viz)!=0:
            datavalid=True
        else:
            sg.popup('At least one box must be checked')
    
    #Choosing the plot to produce        
    plot_to_viz=[]
    datavalid=False
    while datavalid==False:
        layout=[]
        layout += [sg.Text('Which plots do you want to draw ? ')],
               
        for i in range(int(np.ceil(len(plot_list)/2))): #Choice on 2 colums to reduce window width
            try:
                layout+=[sg.CBox(plot_list[2*i],size=(20,1), default=True,key=plot_list[2*i]),sg.CBox(plot_list[2*i+1],size=(20,1), default=True,key=plot_list[2*i+1])],
            except:
                layout+=[sg.CBox(plot_list[2*i],size=(20,1), default=True,key=plot_list[2*i])],    
            
        layout+=[[sg.OK(), sg.Cancel()]]
        
        window = sg.Window('Choosing plot to view', layout)
        event, values = window.read()
        window.close()
        
        if event==sg.WIN_CLOSED or event=='Cancel':
             exit()
        
        plot_to_viz=values
        
        plots=0
        for value in plot_to_viz.values():
            if value==True:
                datavalid=True
                plots+=1

        if datavalid==False:
            sg.popup('At least one box must be checked')
           

                    #SECTION 4 PRODUCING PLOTS
    layout = [[sg.Text('Path to save plots')],
              [sg.Input(default_text='Plots'), sg.FolderBrowse()],
              [sg.Ok(),sg.Cancel()]]
    
    window = sg.Window('Saving plot', layout)
    
    event,values=window.read()
    window.close()
  
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()  
    
    savepath=values[0]    
    
    layout = [[sg.Text('Current progress')],
              [sg.Output(size=(80,12))],
              [sg.ProgressBar(plots, orientation='h', size=(51, 20), key='progressbar')],
              [sg.Cancel()]]
    
    window = sg.Window('Progress', layout)
    progress_bar = window['progressbar']
    plot_done=0
    
    
    event,values=window.read(timeout=5)
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()
    
    if plot_to_viz['Production seasons']==True:
        fig_prod_m=production_season(raw,start_year,end_year,type_to_viz,contrast_colors)
        plot_done+=1
        progress_bar.UpdateBar(plot_done)
    
    event,values=window.read(timeout=5)
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()
    
    if plot_to_viz['Production years']==True:
        fig_prod_y=production_year(raw,start_year,end_year,type_to_viz,contrast_colors)
        plot_done+=1
        progress_bar.UpdateBar(plot_done)
    
    event,values=window.read(timeout=5)
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()

    if plot_to_viz['Studio production']==True:
        fig_studprod=production_studio(raw,start_year,end_year,type_to_viz,contrast_colors)
        plot_done+=1
        progress_bar.UpdateBar(plot_done)   
        
    event,values=window.read(timeout=5)
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()  

    if plot_to_viz['Studios quantity']==True:
        fig_studquant=studio_quantity(raw,start_year,end_year,type_to_viz,contrast_colors)
        plot_done+=1
        progress_bar.UpdateBar(plot_done)   
        
    event,values=window.read(timeout=5)
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()        

    if plot_to_viz['Source repartition']==True:    
        fig_source=source(raw,start_year,end_year,type_to_viz,contrast_colors,2.5)
        plot_done+=1
        progress_bar.UpdateBar(plot_done)
    
    event,values=window.read(timeout=5)
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()
        
    if plot_to_viz['Score distribution']==True:    
        fig_score=score_repartition(raw,start_year,end_year,type_to_viz)
        plot_done+=1
        progress_bar.UpdateBar(plot_done)
    
    event,values=window.read(timeout=5)
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()

    if plot_to_viz['TV (New) length']==True:    
        fig_ep=episode(raw,start_year,end_year,'TV (New)',60)
        plot_done+=1
        progress_bar.UpdateBar(plot_done)
    
    event,values=window.read(timeout=5)
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()
        
    if plot_to_viz['TV (Continuing) length']==True:    
        fig_ep=episode(raw,start_year,end_year,'TV (Continuing)',150)
        plot_done+=1
        progress_bar.UpdateBar(plot_done)
    
    event,values=window.read(timeout=5)
    if event==sg.WIN_CLOSED or event=='Cancel':
        window.close()
        exit()
    
    window.close()    
    sg.popup('Finished ! \nPlots saved at '+savepath)
    
    layout=[[sg.Text('Do you want to draw other plots ?')],
            [sg.Yes(),sg.No()]]
    
    window=sg.Window('Again ?',layout)
    again=window.read()
    window.close()