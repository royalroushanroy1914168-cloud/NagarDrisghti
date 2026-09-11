def calculate_priority(severity, traffic_level=5, vulnerability=5, urgency=5):
    severity_values={"LOW":30,"MEDIUM":50,"HIGH":80,"CRITICAL":100}
    severity_score=severity_values.get(severity.upper(),50)
    score=(severity_score*0.40)+(traffic_level*10*0.25)+(vulnerability*10*0.20)+(urgency*10*0.15)
    return min(100,max(0,round(score)))