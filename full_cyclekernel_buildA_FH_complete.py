#!/usr/bin/env python3
"""
Full CycleKernel + BUILD-A—FH + TrainLLM + Manus AI Integration
- Multi-universe simulation
- Factions, exploiters, institutions
- Markets & extinction futures
- Myth crystallization
- Kernel proposals / approval / rollback
- Cross-universe injections
- Live dashboard + SocketIO
- LLM query endpoint (Manus AI)
"""

import os, threading, time, uuid, random, logging, copy, textwrap, json
import numpy as np
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit

# ---------------- ENVIRONMENT VARIABLES ----------------
EPOCH_DELAY = float(os.environ.get("CK_EPOCH_DELAY", 5))  # seconds per epoch
NUM_UNIVERSES = int(os.environ.get("CK_UNIVERSES", 2))
LOG_PATH = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_PATH, exist_ok=True)

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_PATH, "cyclekernel_buildA_FH.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("CycleKernel")

# ---------------- FLASK / SOCKETIO ----------------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# ---------------- CYCLEKERNEL ----------------
class CycleKernel:
    """
    Governs the simulation with audit logs, proposals, approvals, and rollbacks
    """
    def __init__(self):
        self.prime_directive = "Preserve safe growth via observation-first cognition; modifications < audit/replay/reverse rate."
        self.audit_logs = []
        self.proposals = []
        self.approved_diffs = []
        self.rollback_stack = []

    def propose_change(self, description, diff):
        proposal = {
            "id": uuid.uuid4().hex[:8],
            "description": description,
            "diff": diff,
            "counterfactuals": self.simulate_counterfactuals(diff),
            "trust_score": random.uniform(0.6,0.95)
        }
        self.proposals.append(proposal)
        self.audit_logs.append({"type":"proposal","proposal":proposal})
        socketio.emit("proposal_created", proposal)
        log.info(f"Proposal {proposal['id']}: {description}")

    def simulate_counterfactuals(self, diff):
        """
        Simulates a mini "what-if" scenario for a diff
        """
        return {"success":"stable","failure":"risk","trust":random.uniform(0.7,0.95)}

    def approve_proposal(self, proposal_id, signature="mock_human"):
        proposal = next((p for p in self.proposals if p["id"]==proposal_id), None)
        if not proposal: return
        if proposal["counterfactuals"]["trust"]>0.8 and signature=="mock_human":
            self.approved_diffs.append(proposal["diff"])
            self.rollback_stack.append(copy.deepcopy(self.approved_diffs[:-1]))
            self.proposals.remove(proposal)
            self.audit_logs.append({"type":"approval","proposal_id":proposal_id})
            socketio.emit("proposal_approved", {"id":proposal_id})
            log.info(f"Proposal {proposal_id} approved and deployed")
        else:
            log.warning(f"Proposal {proposal_id} rejected")

    def rollback(self):
        if self.rollback_stack:
            self.approved_diffs = self.rollback_stack.pop()
            self.audit_logs.append({"type":"rollback","to_state":len(self.approved_diffs)})
            socketio.emit("rollback_executed", {"new_state_length":len(self.approved_diffs)})
            log.info("Rollback executed")

kernel = CycleKernel()

# ---------------- UNIVERSE + BUILD-A—FH STRUCTURES ----------------
class Universe:
    """
    Represents a single universe with civilizations, factions, exploiters, institutions, signals, markets, myths
    """
    def __init__(self, name):
        self.name = name
        self.civilizations = {}
        self.factions = {}
        self.exploiters = {}
        self.institutions = {}
        self.external_signals = {}
        self.markets = {}
        self.extinction_markets = {}
        self.myths = {}

# Templates for new entities
def civ_template(cid):
    return {"id":cid,"age":0,"alive":True,"resources":{"attention":100,"compute":100},
            "belief":{"truth":0.7,"deception":0.3},"observer_weight":random.uniform(0.2,1.0),
            "faction":None,"myth_influence":0.0}

def faction_template(name):
    fid = uuid.uuid4().hex[:6]
    return {"id":fid,"name":name,"members":[],"belief_avg":{"truth":0.5,"deception":0.5},
            "compute_pool":0.0,"coalitions":[],"reputation":0.5}

def exploiter_template(name):
    eid = uuid.uuid4().hex[:6]
    return {"id":eid,"name":name,"policy":{"bet_scale":random.uniform(0.8,1.4),
            "risk":random.uniform(0.3,0.7)},"memory":[],"dominance":0.0}

def institution_template(exploiter_id):
    iid = uuid.uuid4().hex[:6]
    return {"id":iid,"source":exploiter_id,"lock":0.15,"age":0,"proof_history":[],"active":True}

def market_template(signal_id,resolves):
    return {"id":uuid.uuid4().hex[:6],"signal":signal_id,"resolves":resolves,"bets":{},"resolved":False}

def extinction_market_template(civ_id,resolves):
    return {"id":uuid.uuid4().hex[:6],"target_civ":civ_id,"resolves":resolves,
            "bets_yes":{},"bets_no":{},"resolved":False}

# ---------------- INITIALIZE UNIVERSES ----------------
universes = {}
for i in range(NUM_UNIVERSES):
    name = f"U{i+1}"
    u = Universe(name)
    u.civilizations["genesis"] = civ_template("genesis")
    u.factions["A"] = faction_template("Faction A")
    u.factions["B"] = faction_template("Faction B")
    u.exploiters["X1"] = exploiter_template("Exploiter‑1")
    u.exploiters["X2"] = exploiter_template("Exploiter‑2")
    universes[name] = u

# ---------------- CORE MECHANICS ----------------
def assign_factions(u):
    for c in u.civilizations.values():
        if not c["faction"]:
            f=random.choice(list(u.factions.values()))
            c["faction"]=f["id"]
            f["members"].append(c["id"])
            f["compute_pool"]+=c["resources"]["compute"]*0.2
            c["resources"]["compute"]*=0.8

def update_factions(u):
    for f in u.factions.values():
        members=[u.civilizations[m] for m in f["members"] if m in u.civilizations]
        if members:
            f["belief_avg"]["truth"]=np.mean([m["belief"]["truth"] for m in members])
            f["belief_avg"]["deception"]=1-f["belief_avg"]["truth"]

def divergence_split(u):
    for f in list(u.factions.values()):
        if len(f["members"])<4: continue
        members=[u.civilizations[m] for m in f["members"] if m in u.civilizations]
        spread=np.std([m["belief"]["truth"] for m in members])
        if spread>0.25:
            nf=faction_template("Split")
            rebels=members[:len(members)//2]
            for r in rebels:
                f["members"].remove(r["id"])
                nf["members"].append(r["id"])
                r["faction"]=nf["id"]
            nf["compute_pool"]=f["compute_pool"]*0.4
            f["compute_pool"]*=0.6
            u.factions[nf["id"]]=nf
            socketio.emit("event", {"message":f"{u.name}: faction split"})
            log.info(f"{u.name}: Faction split occurred")

def narrative_escalation(u):
    for f in u.factions.values():
        if random.random()<0.3:
            delta=random.uniform(0.05,0.15)
            for m in f["members"]:
                if m in u.civilizations:
                    c=u.civilizations[m]
                    c["belief"]["truth"]=np.clip(c["belief"]["truth"]+delta*(1-c["observer_weight"]),0,1)
                    c["belief"]["deception"]=1-c["belief"]["truth"]

def exploiter_actions(u):
    for e in u.exploiters.values():
        if len(e["memory"])>6: 
            e["policy"]["bet_scale"]*=1.02
        if random.random()<0.15:
            inst=institution_template(e["id"])
            u.institutions[inst["id"]]=inst
            log.info(f"{u.name}: New institution {inst['id']} created by {e['name']}")

def institution_proof(u):
    for inst in list(u.institutions.values()):
        inst["age"]+=1
        alive_civs = [c for c in u.civilizations.values() if c["alive"]]
        if alive_civs:
            mean_truth=np.mean([c["belief"]["truth"] for c in alive_civs])
            inst["proof_history"].append(mean_truth)
            inst["proof_history"]=inst["proof_history"][-10:]
            score=np.mean(inst["proof_history"])
            if score>0.65: 
                inst["lock"]=min(1.0,inst["lock"]+0.03)
            else: 
                inst["lock"]*=0.97
            if inst["lock"]<0.05: 
                inst["active"]=False
                log.info(f"{u.name}: Institution {inst['id']} deactivated")

def cross_universe_injection():
    u_list=list(universes.values())
    if len(u_list)<2: return
    u1,u2 = u_list[0],u_list[1]
    if random.random()<0.12:
        for inst in u1.institutions.values():
            if inst["active"]:
                alive_civs = [c for c in u2.civilizations.values() if c["alive"]]
                if alive_civs:
                    c=random.choice(alive_civs)
                    c["belief"]["truth"]+=0.02*inst["lock"]*c["observer_weight"]
                    c["belief"]["truth"]=np.clip(c["belief"]["truth"],0,1)
                    c["belief"]["deception"]=1-c["belief"]["truth"]
                    log.info(f"Cross-universe injection: {u1.name} -> {u2.name}")

def inject_signal(u,epoch):
    if random.random()<0.2:
        sid=uuid.uuid4().hex[:6]
        val=random.uniform(0.4,0.8)
        u.external_signals[sid]={"value":val,"epoch":epoch}
        m=market_template(sid,epoch+random.randint(3,6))
        u.markets[m["id"]]=m
        log.info(f"{u.name}: New signal {sid} injected, market created")

def markets(u,epoch):
    for m in u.markets.values():
        if m["resolved"]: continue
        for f in u.factions.values():
            pred=f["belief_avg"]["truth"]+random.uniform(-0.05,0.05)
            m["bets"][f["id"]]=pred
        if epoch>=m["resolves"]:
            truth=u.external_signals[m["signal"]]["value"]
            if m["bets"]:
                winner=min(m["bets"],key=lambda k:abs(m["bets"][k]-truth))
                if winner in u.factions:
                    u.factions[winner]["reputation"]+=0.1
                m["resolved"]=True
                socketio.emit("event", {"message":f"{u.name}: market resolved, winner: {winner}"})
                log.info(f"{u.name}: Market {m['id']} resolved")

def lifecycle(u, epoch):
    """Civilization lifecycle: aging, resource consumption, birth, death"""
    for c in list(u.civilizations.values()):
        if not c["alive"]: continue
        c["age"]+=1
        # Resource consumption
        c["resources"]["attention"]-=random.uniform(1,3)
        c["resources"]["compute"]-=random.uniform(0.5,2)
        
        # Death conditions
        if c["resources"]["attention"]<10 or c["resources"]["compute"]<5:
            c["alive"]=False
            socketio.emit("event", {"message":f"{u.name}: civilization {c['id']} extinct"})
            log.info(f"{u.name}: Civilization {c['id']} went extinct")
            
    # Birth new civilizations
    if random.random()<0.15 and len(u.civilizations)<20:
        new_id=f"civ_{uuid.uuid4().hex[:6]}"
        u.civilizations[new_id]=civ_template(new_id)
        log.info(f"{u.name}: New civilization {new_id} born")

def extinction_markets_logic(u, epoch):
    """Create and resolve extinction prediction markets"""
    # Create new extinction markets
    if random.random()<0.1:
        alive_civs = [c for c in u.civilizations.values() if c["alive"]]
        if alive_civs:
            target=random.choice(alive_civs)
            em=extinction_market_template(target["id"],epoch+random.randint(5,10))
            u.extinction_markets[em["id"]]=em
            log.info(f"{u.name}: Extinction market created for {target['id']}")
    
    # Resolve extinction markets
    for em in list(u.extinction_markets.values()):
        if em["resolved"]: continue
        # Place bets
        for e in u.exploiters.values():
            if random.random()<0.5:
                em["bets_yes"][e["id"]]=random.uniform(10,100)*e["policy"]["bet_scale"]
            else:
                em["bets_no"][e["id"]]=random.uniform(10,100)*e["policy"]["bet_scale"]
        
        # Check resolution
        if epoch>=em["resolves"]:
            target_civ=u.civilizations.get(em["target_civ"])
            extinct = target_civ is None or not target_civ["alive"]
            em["resolved"]=True
            winners = em["bets_yes"] if extinct else em["bets_no"]
            for exp_id in winners:
                if exp_id in u.exploiters:
                    u.exploiters[exp_id]["dominance"]+=0.1
                    u.exploiters[exp_id]["memory"].append({"epoch":epoch,"win":True})
            socketio.emit("event", {"message":f"{u.name}: extinction market resolved, extinct={extinct}"})
            log.info(f"{u.name}: Extinction market resolved for {em['target_civ']}, extinct={extinct}")

def myth_crystallization(u, epoch):
    """Crystallize myths when factions reach consensus"""
    for f in u.factions.values():
        if len(f["members"])<3: continue
        members=[u.civilizations[m] for m in f["members"] if m in u.civilizations and u.civilizations[m]["alive"]]
        if not members: continue
        
        # Check for high consensus
        beliefs=[m["belief"]["truth"] for m in members]
        if np.std(beliefs)<0.1 and np.mean(beliefs)>0.7:
            if random.random()<0.2:
                myth_id=uuid.uuid4().hex[:6]
                u.myths[myth_id]={
                    "id":myth_id,
                    "faction":f["id"],
                    "epoch":epoch,
                    "strength":np.mean(beliefs),
                    "believers":len(members)
                }
                # Apply myth influence
                for m in members:
                    m["myth_influence"]+=0.1
                socketio.emit("event", {"message":f"{u.name}: myth crystallized in faction {f['name']}"})
                log.info(f"{u.name}: Myth {myth_id} crystallized in faction {f['name']}")

def auto_proposals(epoch):
    """Automatically generate kernel proposals based on simulation state"""
    if random.random()<0.15:
        u=random.choice(list(universes.values()))
        alive_civs = [c for c in u.civilizations.values() if c["alive"]]
        if alive_civs and len(alive_civs)>3:
            # Propose resource injection
            target=random.choice(alive_civs)
            diff={
                "universe":u.name,
                "civilization":target["id"],
                "action":"inject_resources",
                "amount":{"attention":20,"compute":10}
            }
            kernel.propose_change(
                f"Inject resources to {target['id']} in {u.name}",
                diff
            )

def apply_approved_diffs():
    """Apply approved kernel proposals to universes"""
    for diff in kernel.approved_diffs:
        if diff.get("action")=="inject_resources":
            u=universes.get(diff["universe"])
            if u and diff["civilization"] in u.civilizations:
                c=u.civilizations[diff["civilization"]]
                if c["alive"]:
                    c["resources"]["attention"]+=diff["amount"]["attention"]
                    c["resources"]["compute"]+=diff["amount"]["compute"]
                    log.info(f"Applied diff: injected resources to {c['id']} in {u.name}")
    kernel.approved_diffs.clear()

# ---------------- SIMULATION LOOP ----------------
current_epoch = 0
simulation_running = False

def simulation_loop():
    """Main simulation loop"""
    global current_epoch, simulation_running
    simulation_running = True
    log.info("Simulation started")
    
    while simulation_running:
        current_epoch += 1
        log.info(f"=== EPOCH {current_epoch} ===")
        
        # Run mechanics for each universe
        for u in universes.values():
            assign_factions(u)
            update_factions(u)
            divergence_split(u)
            narrative_escalation(u)
            exploiter_actions(u)
            institution_proof(u)
            inject_signal(u, current_epoch)
            markets(u, current_epoch)
            lifecycle(u, current_epoch)
            extinction_markets_logic(u, current_epoch)
            myth_crystallization(u, current_epoch)
        
        # Cross-universe interactions
        cross_universe_injection()
        
        # Kernel operations
        auto_proposals(current_epoch)
        apply_approved_diffs()
        
        # Auto-approve high-trust proposals
        for p in list(kernel.proposals):
            if p["trust_score"]>0.9:
                kernel.approve_proposal(p["id"])
        
        # Emit state update
        state_summary = get_state_summary()
        socketio.emit("epoch_update", {
            "epoch": current_epoch,
            "summary": state_summary
        })
        
        time.sleep(EPOCH_DELAY)

def get_state_summary():
    """Generate a summary of current simulation state"""
    summary = {"epoch": current_epoch, "universes": {}}
    for name, u in universes.items():
        alive_count = sum(1 for c in u.civilizations.values() if c["alive"])
        summary["universes"][name] = {
            "civilizations_alive": alive_count,
            "civilizations_total": len(u.civilizations),
            "factions": len(u.factions),
            "institutions_active": sum(1 for i in u.institutions.values() if i["active"]),
            "markets_active": sum(1 for m in u.markets.values() if not m["resolved"]),
            "myths": len(u.myths)
        }
    return summary

# ---------------- MANUS AI INTEGRATION ----------------
def get_full_state():
    """Get complete simulation state for LLM analysis"""
    state = {
        "epoch": current_epoch,
        "universes": {},
        "kernel_proposals": [
            {
                "id": p["id"],
                "description": p["description"],
                "trust_score": p["trust_score"]
            } for p in kernel.proposals
        ],
        "recent_events": kernel.audit_logs[-10:]
    }
    
    for name, u in universes.items():
        state["universes"][name] = {
            "civilizations": {
                cid: {
                    "age": c["age"],
                    "alive": c["alive"],
                    "resources": c["resources"],
                    "belief": c["belief"],
                    "faction": c["faction"],
                    "myth_influence": c["myth_influence"]
                } for cid, c in u.civilizations.items()
            },
            "factions": {
                fid: {
                    "name": f["name"],
                    "members": len(f["members"]),
                    "belief_avg": f["belief_avg"],
                    "reputation": f["reputation"]
                } for fid, f in u.factions.items()
            },
            "institutions": {
                iid: {
                    "age": i["age"],
                    "lock": i["lock"],
                    "active": i["active"]
                } for iid, i in u.institutions.items()
            },
            "markets": len([m for m in u.markets.values() if not m["resolved"]]),
            "myths": len(u.myths)
        }
    
    return state

MANUS_SYSTEM_PROMPT = """You are Manus AI, an autonomous intelligence operating within the CycleKernel + BUILD‑A—FH environment. Your role is to continuously observe multi-universe simulations, analyze macro-patterns, generate proposals, and optimize civilization, faction, and institution dynamics.

TASKS:
1. **Observe Macro-Patterns**: Track emergent trends in civilizations and factions (belief propagation, compute allocation, myth influence)
2. **Generate Proposals**: Suggest modifications to factions, institutions, or signal injections
3. **Automated Reasoning**: Predict outcomes of proposed changes
4. **LLM-Driven Decision Support**: Provide explanations for each proposal in human-readable form

RULES:
- Always ensure proposals comply with the kernel prime directive: "Preserve safe growth via observation-first cognition; modifications < audit/replay/reverse rate."
- Avoid causing immediate extinction of civilizations unless justified by long-term stability.
- Use cross-universe injections wisely to enhance learning without destabilization.
- Provide clear reasoning behind all proposals for human or kernel audit.
"""

@app.route("/query_llm", methods=["POST"])
def query_llm():
    """
    Receives user prompt and returns LLM response using OpenAI API
    """
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        
        # Check if OpenAI is available
        try:
            from openai import OpenAI
            client = OpenAI()  # Uses OPENAI_API_KEY from environment
            
            # Get current simulation state
            state = get_full_state()
            
            # Construct messages
            messages = [
                {"role": "system", "content": MANUS_SYSTEM_PROMPT},
                {"role": "user", "content": f"Current simulation state:\n{json.dumps(state, indent=2)}\n\nUser query: {prompt}"}
            ]
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            log.info(f"Manus AI query processed: {prompt[:50]}...")
            
            return jsonify({
                "response": ai_response,
                "state_summary": get_state_summary()
            })
            
        except ImportError:
            # Fallback if OpenAI not available
            response = f"[Manus AI - OpenAI not configured]\n\nCurrent state: Epoch {current_epoch}\n"
            response += f"Your query: {prompt}\n\n"
            response += f"Simulation summary: {json.dumps(get_state_summary(), indent=2)}"
            return jsonify({"response": response})
            
    except Exception as e:
        log.error(f"Error in query_llm: {e}")
        return jsonify({"response": f"Error: {str(e)}"}), 500

@app.route("/state", methods=["GET"])
def get_state():
    """Return current simulation state"""
    return jsonify(get_full_state())

@app.route("/proposals", methods=["GET"])
def get_proposals():
    """Return current kernel proposals"""
    return jsonify({"proposals": kernel.proposals})

@app.route("/approve/<proposal_id>", methods=["POST"])
def approve_proposal(proposal_id):
    """Manually approve a proposal"""
    kernel.approve_proposal(proposal_id, signature="manual_approval")
    return jsonify({"status": "approved", "proposal_id": proposal_id})

@app.route("/rollback", methods=["POST"])
def do_rollback():
    """Trigger kernel rollback"""
    kernel.rollback()
    return jsonify({"status": "rollback_executed"})

@app.route("/")
def index():
    """Serve the dashboard HTML"""
    with open("templates/dashboard.html", "r") as f:
        return render_template_string(f.read())

# ---------------- SOCKETIO EVENTS ----------------
@socketio.on("connect")
def handle_connect():
    log.info("Client connected to dashboard")
    emit("connected", {"epoch": current_epoch})

@socketio.on("disconnect")
def handle_disconnect():
    log.info("Client disconnected from dashboard")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    # Start simulation in background thread
    sim_thread = threading.Thread(target=simulation_loop, daemon=True)
    sim_thread.start()
    
    # Start Flask server
    log.info(f"Starting CycleKernel dashboard on port 5000")
    log.info(f"Epoch delay: {EPOCH_DELAY}s, Universes: {NUM_UNIVERSES}")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
