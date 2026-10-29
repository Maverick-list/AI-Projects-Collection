
try:
    import mediapipe.python.solutions.hands as mp_hands
    print("Import success")
    print(mp_hands)
except ImportError as e:
    print("ImportError:", e)
except AttributeError as e:
    print("AttributeError:", e)
