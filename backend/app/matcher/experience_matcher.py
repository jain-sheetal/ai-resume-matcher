def evaluate_experience(candidate_years: float, required_years: float) -> float:
    """
    Evaluate candidate years of experience against JD requirement.
    Returns a score from 0.0 to 100.0.
    """
    if required_years <= 0.0:
        return 100.0

    if candidate_years >= required_years:
        # Meets or exceeds requirements
        return 100.0
    else:
        # Prorated score based on proportion completed
        ratio = max(0.0, candidate_years / required_years)
        # Apply a smooth progressive scale so 2/3 years gives ~70% rather than overly harsh cutoff
        score = (ratio ** 0.85) * 100.0
        return round(min(100.0, max(10.0, score)), 1)
