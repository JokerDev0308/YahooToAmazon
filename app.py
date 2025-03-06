import streamlit as st
from pathlib import Path
from session_manager import SessionManager
import config

# Constants
PAGE_CONFIG = {
    "page_title": "YahooToAmazon",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Custom CSS
LOGIN_STYLE = """
    <style>
        #login{
            text-align:center;
        }
        .stButton{
            text-align:center;
        }
        .stButton>button{
            min-width:7rem;
        }
    </style>
"""

class App:
    def __init__(self):
        self.session_manager = SessionManager()
        self.initialize_session_state()
        self.setup_page_config()
        
        
    @staticmethod
    def initialize_session_state():
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False
            
    @staticmethod
    def setup_page_config():
        st.set_page_config(**PAGE_CONFIG)
        
    def logout(self):
        st.session_state.logged_in = False
        config.CURRENT_USER = None

        
    def get_pages(self):
        return [
            st.Page("home.py", title="ホーム", icon="🏠"),
            st.Page("settings.py", title="設定", icon= "⚙️"),
        ]
        
    def authenticate(self, username: str, password: str) -> bool:
        if self.session_manager.validate_user(username, password):
            config.CURRENT_USER = username
            return True
        return False
    
    def show_login_modal(self):
        col1, col2, col3 = st.columns(3)
        with col2:
            with st.container(border=True):
                st.markdown(LOGIN_STYLE, unsafe_allow_html=True)
                st.subheader("ログイン")
                
                username = st.text_input("ユーザー名")
                password = st.text_input("パスワード", type="password")
                
                if st.button("ログイン"):
                    if self.authenticate(username, password):
                        st.session_state.logged_in = True
                        st.toast("ログインに成功しました!")
                        st.rerun()
                    else:
                        st.error("ユーザー名またはパスワードが無効です。")
    
    def run(self):
        if st.session_state.logged_in:
            st.navigation(self.get_pages()).run()
            st.sidebar.button('ログアウト', on_click=self.logout, use_container_width=True, key='logout')
        else:
            self.show_login_modal()

if __name__ == "__main__":
    app = App()
    app.run()
