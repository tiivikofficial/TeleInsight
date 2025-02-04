# 📦 Telegram Channel Activity Analyzer
# ✨ Final Version with Full Capabilities
# 🔗 Requirement: Python 3.10+

import os
import asyncio
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel

# 🔐 Configuration Settings
class Config:
    API_ID = 'YOUR_API_ID'          # Get from my.telegram.org
    API_HASH = 'YOUR_API_HASH'      # Get from my.telegram.org
    CHANNEL = 'channel_username'    # Target channel username
    SESSION_NAME = 'channel_analyzer'
    PLOT_SAVE_PATH = './plots/'

# 📈 Main Analyzer Class
class TelegramChannelAnalyzer:
    def __init__(self):
        self.client = None
        self.channel = None
        self.all_messages = []
        
    async def initialize(self):
        """Connect to Telegram API"""
        self.client = TelegramClient(
            Config.SESSION_NAME,
            Config.API_ID,
            Config.API_HASH
        )
        await self.client.start()
        self.channel = await self.client.get_entity(Config.CHANNEL)
        
    async def fetch_messages(self, limit=5000):
        """Fetch message history with pagination"""
        print('🔍 Starting message retrieval...')
        offset_id = 0
        total_messages = 0
        
        while True:
            history = await self.client(GetHistoryRequest(
                peer=self.channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=100,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break
                
            self.all_messages.extend(history.messages)
            total_messages += len(history.messages)
            offset_id = history.messages[-1].id
            
            if total_messages >= limit:
                break
                
            print(f'📥 {total_messages} messages fetched...')
            await asyncio.sleep(1)
            
        print(f'✅ Total {len(self.all_messages)} messages retrieved')
        
    def analyze_data(self):
        """Comprehensive data analysis and visualization"""
        if not self.all_messages:
            raise ValueError("No data available for analysis")
            
        os.makedirs(Config.PLOT_SAVE_PATH, exist_ok=True)
        
        # 🗃 Create DataFrame
        df = pd.DataFrame([{
            'id': msg.id,
            'date': msg.date,
            'views': msg.views or 0,
            'replies': msg.replies.replies if msg.replies else 0,
            'forwards': msg.forwards or 0,
            'media': 1 if msg.media else 0
        } for msg in self.all_messages])
        
        # 📊 Time-based Analysis
        self._plot_time_analysis(df)
        
        # 📈 Engagement Analysis
        self._plot_engagement_analysis(df)
        
        # 📌 Content Analysis
        self._plot_content_analysis(df)
        
        return df
        
    def _plot_time_analysis(self, df):
        """Temporal activity analysis"""
        plt.figure(figsize=(15, 8))
        
        # Daily activity
        daily = df.resample('D', on='date').size()
        daily.plot(kind='line', title='Daily Activity', color='purple')
        plt.savefig(f'{Config.PLOT_SAVE_PATH}daily_activity.png')
        plt.clf()
        
        # Peak hours
        df['hour'] = df['date'].dt.hour
        hourly = df.groupby('hour').size()
        hourly.plot(kind='bar', title='Hourly Activity', color='orange')
        plt.savefig(f'{Config.PLOT_SAVE_PATH}hourly_activity.png')
        plt.clf()
        
    def _plot_engagement_analysis(self, df):
        """User engagement analysis"""
        plt.figure(figsize=(15, 8))
        
        # Engagement comparison
        engagement = df[['views', 'replies', 'forwards']].sum()
        engagement.plot(kind='pie', autopct='%1.1f%%', 
                       colors=['#ff9999','#66b3ff','#99ff99'],
                       title='Engagement Distribution')
        plt.savefig(f'{Config.PLOT_SAVE_PATH}engagement_dist.png')
        plt.clf()
        
        # Engagement trend
        df.set_index('date')[['views', 'replies']].resample('W').mean().plot(
            title='Weekly Engagement Trend'
        )
        plt.savefig(f'{Config.PLOT_SAVE_PATH}engagement_trend.png')
        plt.clf()
        
    def _plot_content_analysis(self, df):
        """Content type analysis"""
        plt.figure(figsize=(10,6))
        
        media_ratio = df['media'].value_counts(normalize=True)
        media_ratio.plot(kind='bar', 
                        title='Media Content Ratio',
                        color=['skyblue', 'lightgreen'])
        plt.xticks([0,1], ['Text', 'Media'], rotation=0)
        plt.savefig(f'{Config.PLOT_SAVE_PATH}media_analysis.png')
        plt.clf()

# 🚀 Main Execution
async def main():
    analyzer = TelegramChannelAnalyzer()
    await analyzer.initialize()
    await analyzer.fetch_messages(limit=2000)
    
    print('📊 Starting data analysis...')
    df = analyzer.analyze_data()
    
    print('🎉 Analysis complete! Results saved in plots folder')
    print("\n📝 Statistical Summary:")
    print(df.describe())

if __name__ == '__main__':
    asyncio.run(main())
