from app.rag import chunk_text

def test_chunk_overlap():
    words=" ".join(f"w{i}" for i in range(2000))
    chunks=chunk_text(words,size=100,overlap=10)
    assert len(chunks)>1
    assert chunks[0].split()[-10:]==chunks[1].split()[:10]
