import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Douglas-Peucker PPFG",
    page_icon=":rocket:",
    
    menu_items={
        'About': """
            ## Douglas Pecker 
            This application was made to decimate the PPFG 
            
            **Created by:** Morten Vier Simensen  
            **Contact:** Morten.vier.simensen@akerbp.com
        """
    }
)

def plot(df):
    fig = go.Figure()
    columns_to_plot = df.columns
    # Add traces for each selected column
    for column in df:
        fig.add_trace(
            go.Scatter(
                x=df[column],  # X values from selected column
                y=df.index,    # Y values from Depth (index)
                name=column,
                mode='lines',
                line=dict(shape='linear')
            )
        )

    button_all = dict(label='Show All',
                      method='update',
                      args=[{'visible': [True] * len(columns_to_plot)},
                            {'title': 'Show All'}])

    def create_layout_button(column):
        return dict(label=column,
                    method='update',
                    args=[{'visible': [column == col for col in columns_to_plot]},
                          {'title': column}])

    all_buttons = [button_all] + [create_layout_button(column) for column in columns_to_plot]

    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
            active=0,
            buttons=all_buttons
        )],
        showlegend=True,
        xaxis_title="Pressure [bara]",  # X-axis title
        yaxis_title="Depth",            # Y-axis title
        height=850
    )
    fig = st.plotly_chart(fig, use_container_width=True)
    return fig 


def plot_with_points(df2, df):
    fig = go.Figure()
    columns_to_plot = df.columns
        # Add traces for each selected column
    for column in df:
        fig.add_trace(
            go.Scatter(
                x=df[column],  # X values from selected column
                y=df.index,    # Y values from Depth (index)
                name=column,
                mode='lines',
                line=dict(shape='linear')
            )
        )


    for column in df2:
        fig.add_trace(
            go.Scatter(
                x=df2[column],  # X values from selected column
                y=df2.index,    # Y values from Depth (index)
                name=column,
                mode='markers',  # Display as markers (bullet points)
                marker=dict(size=8)
            )
        )

    button_all = dict(label='Show All',
                      method='update',
                      args=[{'visible': [True] * len(columns_to_plot)},
                            {'title': 'Show All'}])

    def create_layout_button(column):
        return dict(label=column,
                    method='update',
                    args=[{'visible': [column == col for col in columns_to_plot]},
                          {'title': column}])

    all_buttons = [button_all] + [create_layout_button(column) for column in columns_to_plot]

    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
            active=0,
            buttons=all_buttons
        )],
        showlegend=True,
        xaxis_title="Pressure [bara]",  # X-axis title
        yaxis_title="Depth",            # Y-axis title
        height=850
    )
    fig = st.plotly_chart(fig, use_container_width=True)
    return fig 



st.title("Douglas-Peucker for PPFG")
uploaded_file = st.file_uploader("Upload PPFG Excel file (Column names in row 1 with data below. Remove all other info from the excel file)", type=["xlsx", "xls"])
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, dtype = 'float64')
    except:
        df = pd.read_excel(uploaded_file, dtype = 'float64', decimal=',')
    
    try:
        df.set_index('Depth', inplace=True)
    except KeyError:
        try:
            df.set_index('depth', inplace=True)
        except KeyError:
            df.set_index(df.columns[0], inplace=True)
    df.replace(-999.25, np.nan, inplace=True)
    st.write("Uploaded PPFG Data")
    st.dataframe(df)
    st.write("-999.25 treated as Nan")  
    fig1 = plot(df)

    from rdp import rdp
    st.write("Adjust epsilon with slider, or specify below")
    epsilon = st.slider(label="Epsilon", value=0.05, min_value=0.0, max_value=0.15, step=0.001)
    epsilon = float(st.text_input(label="Epsilon", value=epsilon))
    if epsilon < 0:
        st.error("Epsilon cant be negative")
        st.stop()
    msg = st.warning("Making calculations, have a few seconds patience")
    size = len(df.index)
    df2 = pd.DataFrame(index=df.index, columns=[column for column in df])
    df2[:] = np.nan
    plot_placeholder = st.empty()
    df4 = pd.DataFrame(index = range(size))
    excel_writer = pd.ExcelWriter('PPFG_Douglas_Pecker.xlsx', engine='openpyxl')
    for column in df.columns:
        sub = df[[column]].copy()
        sub['Depth'] = df.index
        sub = sub.dropna()
        points = np.column_stack([sub['Depth'], sub[column]])   
        rdp_PPFG = (rdp(points, epsilon))
        df3 = pd.DataFrame()
        df3.index = rdp_PPFG.T[0]
        df3[column] = rdp_PPFG.T[1]
        df2.update(df3)
        df3.index.names = ["Depth"]
        i = 0
        original_points = len(sub.index)
        simplified_points = len(df3[column])
        reduction_percentage = (1 - simplified_points / original_points) * 100
        st.markdown(f"**{column}**: Number of points reduced from {original_points} to {simplified_points} ({reduction_percentage:.2f}% reduction)")
        st.dataframe(df3)
        i+=3
    with plot_placeholder.container():
        fig2 = plot_with_points(df2, df)
    msg.empty()
st.write(" ")
st.write(" ")
st.write("Created by Morten Vier Simensen")



