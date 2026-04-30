import numpy as np
from sklearn.cluster import KMeans


def get_adaptive_k(n):
    """
    Calcule le nombre de clusters selon n.
    Formule : k = min(3, max(1, n // 15))
    Exemples : n=10→1, n=30→2, n=45→3
    """
    return min(3, max(1, n // 15))


def adaptive_kmeans(X_scaled, n):
    """
    K-Means adaptatif pour segmenter les prix.
    Retourne les labels ou None si n < 10.
    """

    # Pas assez de données
    if n < 10 or X_scaled is None:
        return None

    try:
        # Convertir en numpy array
        data = np.asarray(X_scaled)

        # Forcer le format 2D
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        # Nombre de clusters
        k = get_adaptive_k(n)

        # Modèle KMeans
        model = KMeans(
            n_clusters=k,
            n_init=10,
            random_state=42
        )

        # Entraînement + prédiction
        return model.fit_predict(data)

    except Exception as e:
        print(f"[adaptive_kmeans] Erreur : {e}")
        return None