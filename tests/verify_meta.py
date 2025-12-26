from sem_view.utils.metadata_parser import get_metadata_context
import pprint

def test_metadata():
    context = get_metadata_context("docs/sample.tif")
    print("--- Extracted Context ---")
    pprint.pprint(context)
    
    # Assertions
    assert "Beam Voltage" in context, "Beam Voltage missing"
    assert "Date" in context, "Date missing"
    assert "Mag" in context, "Mag missing"
    assert "x x" not in context["Mag"], "Mag has double 'x'"

if __name__ == "__main__":
    test_metadata()
