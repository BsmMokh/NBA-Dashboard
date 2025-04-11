import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="NBA Players Dashboard",
    page_icon="🏀",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("top_25_nba_players.csv")
    # Add season column (2024-25 season)
    df['season'] = '2024-25'
    return df

# Load the data
df = load_data()

# Sidebar
st.sidebar.title("🏀 NBA Players Dashboard")
st.sidebar.markdown("---")

# Season filter
seasons = sorted(df['season'].unique(), reverse=True)
selected_season = st.sidebar.selectbox("Select Season", seasons)

# Filter data based on season
filtered_df = df[df['season'] == selected_season]

# Player comparison section in sidebar
st.sidebar.markdown("---")
st.sidebar.title("Compare Players")
selected_players = st.sidebar.multiselect(
    "Select Players to Compare",
    options=df['name'].unique(),
    default=df['name'].iloc[:2].tolist()
)

# Position filter
positions = ['All'] + list(df['position'].unique())
selected_position = st.sidebar.selectbox(
    "Filter by Position",
    options=positions,
    index=0
)

# Filter data based on position
if selected_position != 'All':
    filtered_df = filtered_df[filtered_df['position'] == selected_position]

# Main content
st.title("🏀 NBA Players Performance Analysis")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Player Comparison", "Individual Stats", "Position Analysis", "Team Analysis"])

# Tab 1: Player Comparison
with tab1:
    st.header("Player Comparison")
    
    if selected_players:
        st.write(f"Comparing: {', '.join(selected_players)}")
        
        # Get stats for selected players
        comparison_df = filtered_df[filtered_df['name'].isin(selected_players)]
        
        # Create comparison metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Points Per Game", 
                     f"{comparison_df['ppg'].mean():.1f}",
                     f"Max: {comparison_df['ppg'].max():.1f}")
        with col2:
            st.metric("Rebounds Per Game", 
                     f"{comparison_df['rpg'].mean():.1f}",
                     f"Max: {comparison_df['rpg'].max():.1f}")
        with col3:
            st.metric("Assists Per Game", 
                     f"{comparison_df['apg'].mean():.1f}",
                     f"Max: {comparison_df['apg'].max():.1f}")
        
        # Create bar chart for comparison
        comparison_stats = comparison_df[['name', 'ppg', 'rpg', 'apg']].melt(
            id_vars=['name'],
            value_vars=['ppg', 'rpg', 'apg'],
            var_name='Statistic',
            value_name='Value'
        )
        
        fig_comparison = px.bar(
            comparison_stats,
            x='name',
            y='Value',
            color='Statistic',
            barmode='group',
            title='Player Statistics Comparison',
            labels={'Value': 'Value', 'name': 'Player', 'Statistic': 'Statistic'}
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Radar chart for player comparison
        categories = ['ppg', 'rpg', 'apg', 'spg', 'bpg']
        
        fig_radar = go.Figure()
        
        for player in selected_players:
            player_data = comparison_df[comparison_df['name'] == player].iloc[0]
            values = [player_data[cat] for cat in categories]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                name=player,
                fill='toself'
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([max(comparison_df[cat]) for cat in categories])]
                )
            ),
            title="Player Stats Comparison (Radar Chart)"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Please select players to compare from the sidebar.")

# Tab 2: Individual Stats
with tab2:
    st.header("Individual Player Stats")
    
    # Player selection for individual stats
    selected_player = st.selectbox(
        "Select a Player for Detailed Stats",
        options=df['name'].unique(),
        index=0
    )
    
    # Get player stats
    player_stats = df[df['name'] == selected_player].iloc[0]
    
    # Create three columns for key stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Points Per Game", f"{player_stats['ppg']:.1f}")
    with col2:
        st.metric("Rebounds Per Game", f"{player_stats['rpg']:.1f}")
    with col3:
        st.metric("Assists Per Game", f"{player_stats['apg']:.1f}")
    
    # Additional stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Steals Per Game", f"{player_stats['spg']:.1f}")
    with col2:
        st.metric("Blocks Per Game", f"{player_stats['bpg']:.1f}")
    with col3:
        st.metric("Field Goal %", f"{player_stats['fg_pct']:.1f}%")
    with col4:
        st.metric("Efficiency", f"{player_stats['efficiency']:.1f}")
    
    # Player info
    st.subheader("Player Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Team:** {player_stats['team']}")
    with col2:
        st.write(f"**Position:** {player_stats['position']}")
    
    # Bar chart of player stats
    player_stats_chart = pd.DataFrame({
        'Statistic': ['PPG', 'RPG', 'APG', 'SPG', 'BPG'],
        'Value': [player_stats['ppg'], player_stats['rpg'], player_stats['apg'], 
                 player_stats['spg'], player_stats['bpg']]
    })
    
    fig_player = px.bar(
        player_stats_chart,
        x='Statistic',
        y='Value',
        title=f"{selected_player}'s Key Statistics",
        color='Statistic'
    )
    st.plotly_chart(fig_player, use_container_width=True)

# Tab 3: Position Analysis
with tab3:
    st.header("Position Analysis")
    
    # Position distribution
    position_counts = df['position'].value_counts().reset_index()
    position_counts.columns = ['Position', 'Count']
    
    fig_position = px.pie(
        position_counts,
        values='Count',
        names='Position',
        title='Distribution of Players by Position'
    )
    st.plotly_chart(fig_position, use_container_width=True)
    
    # Position stats comparison
    position_stats = df.groupby('position').agg({
        'ppg': 'mean',
        'rpg': 'mean',
        'apg': 'mean',
        'efficiency': 'mean'
    }).reset_index()
    
    # Melt the dataframe for easier plotting
    position_stats_melted = position_stats.melt(
        id_vars=['position'],
        value_vars=['ppg', 'rpg', 'apg', 'efficiency'],
        var_name='Statistic',
        value_name='Value'
    )
    
    fig_position_stats = px.bar(
        position_stats_melted,
        x='position',
        y='Value',
        color='Statistic',
        barmode='group',
        title='Average Statistics by Position',
        labels={'position': 'Position', 'Value': 'Average Value', 'Statistic': 'Statistic'}
    )
    st.plotly_chart(fig_position_stats, use_container_width=True)
    
    # Scatter plot of Points vs Rebounds by Position
    fig_scatter = px.scatter(
        filtered_df,
        x='ppg',
        y='rpg',
        color='position',
        hover_data=['name', 'team'],
        title='Points vs Rebounds by Position',
        labels={'ppg': 'Points Per Game', 'rpg': 'Rebounds Per Game'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# Tab 4: Team Analysis
with tab4:
    st.header("Team Analysis")
    
    # Group by team and calculate average stats
    team_stats = df.groupby('team').agg({
        'ppg': 'mean',
        'rpg': 'mean',
        'apg': 'mean',
        'efficiency': 'mean'
    }).reset_index()
    
    # Create a heatmap of team performance
    fig_heatmap = px.imshow(
        team_stats.set_index('team')[['ppg', 'rpg', 'apg', 'efficiency']],
        title="Team Performance Heatmap",
        labels=dict(x="Statistic", y="Team", color="Value")
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Bar chart of top 10 players by efficiency
    top_10_efficiency = df.nlargest(10, 'efficiency')
    fig_bar = px.bar(
        top_10_efficiency,
        x='name',
        y='efficiency',
        title='Top 10 Players by Efficiency',
        labels={'efficiency': 'Efficiency Score', 'name': 'Player'}
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Team distribution
    team_counts = df['team'].value_counts().reset_index()
    team_counts.columns = ['Team', 'Count']
    
    fig_team = px.bar(
        team_counts,
        x='Team',
        y='Count',
        title='Number of Top 25 Players by Team'
    )
    fig_team.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_team, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Data source: NBA Players Statistics 2024-25 Season") 