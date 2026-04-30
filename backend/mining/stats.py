import statistics  


def compute_stats(prices: list[float]) -> dict:
    
    """
    Calcule les statistiques descriptives pour une liste de prix.

    Les Arguments  :

        prices (list[float]): Liste de valeurs numériques (prix).

    La Resultat comme Dictionnaire contient :

        
            - count    : nombre d'éléments
            - mean     : moyenne arithmétique
            - median   : médiane
            - std      : écart-type (échantillon)
            - variance : variance (échantillon)
            - min      : valeur minimale
            - max      : valeur maximale
            - q1       : premier quartile (25%)
            - q3       : troisième quartile (75%)
            - iqr      : écart interquartile (Q3 - Q1)
    """



    #liste vide 

    if not prices:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "variance": 0.0,
            "min": 0.0,
            "max": 0.0,
            "q1": 0.0,
            "q3": 0.0,
            "iqr": 0.0,
        }

    #metrique de base

    count = len(prices)
    min_val = float(min(prices))
    max_val = float(max(prices))
    mean_val = float(statistics.mean(prices))
    median_val = float(statistics.median(prices))

    # Variance et écart-type
    if count > 1:
        var_val = float(statistics.variance(prices))
        std_val = float(statistics.stdev(prices))
    else:
        var_val = 0.0
        std_val = 0.0


     # Quartiles
    if count >= 2:
        q = statistics.quantiles(prices, n=4)
        q1 = float(q[0])
        q3 = float(q[2])
    else:

        q1 = float(prices[0])
        q3 = float(prices[0])

    iqr = float(q3 - q1)

   # Résultat final
   
    return {
        "count": count,
        "mean": mean_val,
        "median": median_val,
        "std": std_val,
        "variance": var_val,
        "min": min_val,
        "max": max_val,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
    }