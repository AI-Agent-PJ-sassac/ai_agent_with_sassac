
import os
import shutil
from document_loader import load_documents
from vector_store import create_vectorstore, get_db_path

def test_debug():
    # 1. Inspect existing data
    base_data = "data"
    sessions = os.listdir(base_data)
    print(f"Found sessions in data: {sessions}")
    
    target_session = None
    target_file = None
    
    for sess in sessions:
        if sess.startswith("sess_"):
            # Use the first session found
            sess_path = os.path.join(base_data, sess)
            if os.path.exists(sess_path):
                files = os.listdir(sess_path)
                if files:
                    target_session = sess
                    target_file = os.path.join(sess_path, files[0])
                    break
    
    if not target_file:
        print("No uploaded file found to test.")
        return

    print(f"Testing with file: {target_file}")
    
    # 2. Test Loader
    try:
        docs = load_documents(target_file)
        print(f"Loaded {len(docs)} docs.")
        if docs:
            print(f"Sample content: {docs[0].page_content[:100]}")
        else:
            print("Docs list is empty!")
            return
    except Exception as e:
        print(f"Loader failed: {e}")
        return

    # 3. Test Chroma Creation
    test_sess_id = "sess_oat9br3jc_mkfkxqqk"
    print(f"Attempting to create DB for session: {test_sess_id}")
    
    try:
        # Clean up previous test (if any)
        db_path = get_db_path(test_sess_id)
        if os.path.exists(db_path):
            try:
                shutil.rmtree(db_path)
            except:
                pass
            
        store = create_vectorstore(docs, session_id=test_sess_id)
        if store:
            print("Successfully created vectorstore object.")
            # Verify folder exists
            if os.path.exists(db_path):
                 print(f"DB Folder exists at {db_path}")
                 print(f"Contents: {os.listdir(db_path)}")
            else:
                 print(f"CRITICAL: DB Folder DOES NOT EXIST at {db_path}")
        else:
            print("create_vectorstore returned None.")
            
    except Exception as e:
        print(f"Chroma creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug()
