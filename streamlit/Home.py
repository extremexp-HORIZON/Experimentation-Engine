import streamlit as st

def createsidebar():
    st.markdown("""<style>[data-testid=stSidebar] { background-color: #E9FCDB;}</style> """, unsafe_allow_html=True)

    st.sidebar.write(" ")
    st.sidebar.write(" ")

    st.sidebar.image("images/ExtremeXPLogoIcon.png", use_column_width=True)
    st.sidebar.image("images/ExtremeXPLogoText.png", use_column_width=True)

    st.sidebar.write(" ")

    st.sidebar.subheader("About")
    about_text="Our platform is dedicated to optimizing complex data analytics workflows. With the application, you can create workflows, generate workflow variants, and run experiments to refine your analytical processes. Join us and unlock the potential of your analytics journey."
    st.sidebar.markdown(f'<p style="text-align: justify;">{about_text}</p>', unsafe_allow_html=True)

    st.sidebar.write(" ")
    st.sidebar.write(" ")

    st.sidebar.subheader("Version 1.0")
    st.sidebar.subheader("Copyright © 2023 ExtremeXP")

def wide_space_default():
    st.set_page_config(layout="wide")



def main():
    wide_space_default()
    createsidebar()

    st.markdown("<h1 style='font-family: Merriweather, serif;text-align: center; color: #0055BC;'>Welcome to ExtremeXP Experimentation Engine</h1>", unsafe_allow_html=True)
    st.write(" ")
    st.write(" ")

    st.markdown("<p style='text-align: justify; font-size: 18px;'> Our platform is dedicated to optimizing complex data analytics workflows. "
                 "With us, you can create workflows, generate workflow variants, and run experiments to refine your analytical processes. "
                 "Whether you're fine-tuning existing workflows or exploring innovative variants, "
                 "we provide the tools you need for streamlined and efficient data analysis. "
                 "Join us and unlock the potential of your analytics journey.</p>", unsafe_allow_html=True)

    st.write("---")

    st.markdown("<h2 style='color: #38D6A2;'>Key Features</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 16px;'>- Define your own workflows</p>"
                    "<p style='font-size: 16px;'>   - Generate workflow variants</p>"
                    "<p style='font-size: 16px;'>- Run experiments</p>"
                    "<p style='font-size: 16px;'>- Find the best workflow variant for your usecase</p>"
                    "<p style='font-size: 16px;'>- Fine-tune existing workflows</p>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("<h2 style='color: #38D6A2;'>Demo Video</h2>", unsafe_allow_html=True)
    # st.video("ScreenRecordingFull.mp4", start_time=0, subtitles=None, width=200, height=300)
    st.markdown(
        f'<video style="border: 1px solid black;" width=1000 height=400 controls><source src="ScreenRecordingFull.mp4" type="video/mp4"></video>',
        unsafe_allow_html=True,
    )

    st.markdown("[Getting Started](pages/README.MD)")
    st.markdown("[Documentation](#)")
    st.write("---")

    st.markdown("<h2 style='color: #38D6A2;'>Contact & Resources</h2>", unsafe_allow_html=True)
    st.write("For more information, visit our [official website](https://www.extremexp.eu).")

if __name__ == "__main__":
    main()
