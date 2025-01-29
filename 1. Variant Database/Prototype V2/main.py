import streamlit as st
import subprocess

def main():
    st.title("Variant Manager")

    st.write(
        """
        Welcome to the Variant Manager application!  
        Please select an option below to proceed.
        """
    )

    # Buttons for different functionalities
    if st.button("Launch Variant Database"):
        launch_variant_database()

    if st.button("Launch HPO Annotator"):
        launch_hpo_annotator()


def launch_variant_database():
    """Launch Variant Database functionality."""
    try:
        import variant_db  # Ensure variant_db.py exists
        variant_db.main()  # Assuming variant_db.py has a main() function
        st.success("Variant Database launched successfully!")
    except ImportError:
        st.error("Variant Database module (variant_db.py) not found.")
    except AttributeError:
        st.error("Variant Database does not have a `main()` function.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def launch_hpo_annotator():
    """Launch HPO Annotator using Streamlit."""
    try:
        st.write("Launching HPO Annotator...")
        subprocess.run(["streamlit", "run", "app_hpo.py"], check=True)
    except FileNotFoundError:
        st.error("Streamlit is not installed or not in PATH.")
    except subprocess.CalledProcessError as e:
        st.error(f"Streamlit encountered an error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
