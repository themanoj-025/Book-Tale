# Book-Tale — Architecture

```mermaid
graph TB
    subgraph Web ["Flask Web App"]
        A[web_app.py] --> B[page_routes.py]
        A --> C[social_routes.py]
        A --> D[new_features_routes.py]
        A --> E[Socket.io]
    end

    subgraph Auth ["Authentication"]
        F[auth.py] --> G[Session Auth]
        F --> H[Email Verification]
        F --> I[Password Reset]
        F --> J[Role Guard]
    end

    subgraph Core ["Core Services"]
        K[library.py]
        L[book.py]
        M[user.py]
        N[reviews.py]
        O[recommender.py]
        P[realtime.py]
    end

    subgraph Storage ["JSON File Storage"]
        Q[data/books.json]
        R[data/users.json]
        S[data/transactions.json]
        T[data/reservations.json]
        U[backup.py]
    end

    Web --> Auth
    Web --> Core
    Core --> Storage
    Auth --> Storage

    subgraph Features ["Feature Modules"]
        V[gamification.py]
        W[reading_challenge.py]
        X[reading_progress.py]
        Y[notifications.py]
        Z[series.py, lists.py,<br/>wishlist.py, diary.py,<br/>communities.py, social.py]
    end

    Core --> Features
```

## Key Patterns

- **JSON file storage**: No database — all data persisted as JSON files in `data/` directory
- **Backup system**: `backup.py` creates automatic `.bak` copies before write operations
- **Three-tier roles**: member → librarian → admin with progressive permissions
- **Email notifications**: Token-based email verification and password reset (1-hour expiry)
- **Rate limiting**: Login attempt tracking to prevent brute-force attacks
