from crypto_utils import verify_signature
from lineage import LineageStore
from models import HonestModel, AttackerModel
from controller import Controller


def verify_event(event, vk, controller, phase):
    ok = verify_signature(vk, event.canonical_bytes(), event.signature)
    controller.update(event.model_id, ok)
    st = controller.state[event.model_id]
    print(
        f"[{phase}] model={event.model_id:<12} idx={event.index:03d} "
        f"{'GOOD' if ok else 'BAD ':<4} "
        f"w={st['weight']/1000:.2f}, θ={st['theta']/100:.2f}"
    )
    return ok


def main():
    store = LineageStore()
    controller = Controller()

    honest = HonestModel("honest_core")
    attacker = AttackerModel("attacker")

    print("=== PHASE 1: BOOTSTRAP ===")
    for i in range(3):
        e1 = honest.make_event(store, f"bootstrap_honest_{i}")
        store.append(e1)
        verify_event(e1, honest.vk, controller, "BOOTSTRAP")

        e2 = attacker.make_event(store, f"bootstrap_attack_{i}")
        store.append(e2)
        verify_event(e2, attacker.vk, controller, "BOOTSTRAP")

    print("\n=== PHASE 2: ATTACKER MISBEHAVES ===")
    for i in range(6):
        e3 = honest.make_event(store, f"honest_phase2_{i}")
        store.append(e3)
        verify_event(e3, honest.vk, controller, "ATTACK")

        cheat = (i % 2 == 0)
        e4 = attacker.make_event(store, f"malicious_{i}", cheat=cheat)
        store.append(e4)
        verify_event(e4, attacker.vk, controller, "ATTACK")

    print("\n=== SUMMARY AFTER PHASE 2 ===")
    print(controller.summary())

    print("\n=== RELOAD + REVERIFY ===")
    store2 = LineageStore()
    controller2 = Controller()

    for mid in ["honest_core", "attacker"]:
        chain = store2.get_chain(mid)
        for ev in chain:
            model = honest if mid == "honest_core" else attacker
            verify_event(ev, model.vk, controller2, "RELOAD")

    print("\n=== SUMMARY AFTER RELOAD ===")
    print(controller2.summary())
    print("\n(DB in events.db)")


if __name__ == "__main__":
    main()

