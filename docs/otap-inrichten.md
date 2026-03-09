# OTAP inrichten — Softwarecatalogus

## Overzicht

| Omgeving | URL | Namespace | Testdata | TenderNed |
|----------|-----|-----------|----------|-----------|
| **Test (T)** | https://test.softwarecatalogus.vngrealisatie.nl | `softwarecatalogus-test` | Ja (auto) | Demo |
| **Acceptatie (A)** | https://acceptatie.softwarecatalogus.vngrealisatie.nl | `softwarecatalogus-acceptatie` | Nee | Demo |
| **Productie (P)** | https://softwarecatalogus.vngrealisatie.nl | `softwarecatalogus-productie` | Nee | Live |

> De **Ontwikkel (O)** omgeving draait lokaal via `docker-compose up -d` — zie README.

---

## Vereiste GitHub Secrets

Stel deze in via **GitHub → Settings → Environments** (per omgeving apart).

### Per omgeving: `test`, `acceptatie`, `productie`

| Secret | Beschrijving | Voorbeeld |
|--------|--------------|-----------|
| `KUBECONFIG` | Base64-encoded kubeconfig voor de cluster | `$(cat kubeconfig.yaml \| base64 -w 0)` |
| `SECRET_KEY` | Django SECRET_KEY (minimaal 50 tekens, willekeurig) | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `POSTGRES_PASSWORD` | Wachtwoord voor database-gebruiker `swc` | Willekeurig gegenereerd |
| `POSTGRES_ADMIN_PASSWORD` | Wachtwoord voor PostgreSQL superuser | Willekeurig gegenereerd |
| `MEILISEARCH_API_KEY` | Master key voor Meilisearch | `openssl rand -hex 32` |

### Optioneel (alleen indien functie gewenst)

| Secret | Functie |
|--------|---------|
| `ANTHROPIC_API_KEY` | AI-hulpassistent (`/help/vraag/` endpoint) |
| `EMAIL_HOST_PASSWORD` | SMTP-wachtwoord voor e-mailnotificaties |

---

## Secrets doorgeven aan Helm

De secrets worden als `--set` flags meegegeven bij de Helm deploy. Voeg het volgende toe aan het `deploy.yml` workflow bestand onder de Helm deploy stap:

```yaml
- name: Helm deploy
  run: |
    helm upgrade --install \
      softwarecatalogus \
      ./infra/k8s/helm \
      --namespace softwarecatalogus-${{ github.event.inputs.environment }} \
      --create-namespace \
      --set backend.image.tag=${{ github.event.inputs.image_tag }} \
      --set frontend.image.tag=${{ github.event.inputs.image_tag }} \
      --values ./infra/k8s/helm/values-${{ github.event.inputs.environment }}.yaml \
      --set-string "global.secrets.SECRET_KEY=${{ secrets.SECRET_KEY }}" \
      --set-string "global.secrets.POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }}" \
      --set-string "global.secrets.POSTGRES_ADMIN_PASSWORD=${{ secrets.POSTGRES_ADMIN_PASSWORD }}" \
      --set-string "global.secrets.MEILISEARCH_API_KEY=${{ secrets.MEILISEARCH_API_KEY }}" \
      --wait \
      --timeout 5m
```

> **Alternatief (aanbevolen voor productie):** gebruik de [External Secrets Operator](https://external-secrets.io/)
> gekoppeld aan Azure Key Vault, AWS Secrets Manager of HashiCorp Vault.
> Dit voorkomt dat secrets als Helm waarden worden doorgegeven.

---

## Vereiste Kubernetes-infrastructuur

De volgende componenten moeten aanwezig zijn op het Kubernetes cluster (Haven/VNG):

1. **cert-manager** — Voor automatische TLS certificaten (Let's Encrypt)
   ```
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
   ```

2. **ClusterIssuer** — Let's Encrypt staging (test) en prod (acceptatie/productie)
   ```yaml
   # letsencrypt-staging (voor test omgeving)
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-staging
   spec:
     acme:
       server: https://acme-staging-v02.api.letsencrypt.org/directory
       email: beheer@vngrealisatie.nl
       privateKeySecretRef:
         name: letsencrypt-staging
       solvers:
         - http01:
             ingress:
               class: nginx

   # letsencrypt-prod (voor acceptatie + productie)
   apiVersion: cert-manager.io/v1
   kind: ClusterIssuer
   metadata:
     name: letsencrypt-prod
   spec:
     acme:
       server: https://acme-v02.api.letsencrypt.org/directory
       email: beheer@vngrealisatie.nl
       privateKeySecretRef:
         name: letsencrypt-prod
       solvers:
         - http01:
             ingress:
               class: nginx
   ```

3. **Nginx Ingress Controller**
   ```
   helm install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress-nginx --create-namespace
   ```

4. **DNS-records** — Wijs elk subdomein naar het externe IP van de Nginx Ingress:
   ```
   test.softwarecatalogus.vngrealisatie.nl       → <INGRESS_EXTERNAL_IP>
   acceptatie.softwarecatalogus.vngrealisatie.nl → <INGRESS_EXTERNAL_IP>
   softwarecatalogus.vngrealisatie.nl            → <INGRESS_EXTERNAL_IP>
   ```

---

## Eerste deploy uitvoeren

### Test omgeving (met testdata)

1. Push naar `develop` of `main` — CI bouwt automatisch Docker images en pushed naar `ghcr.io`
2. Ga naar **GitHub → Actions → Deploy → Run workflow**
3. Kies:
   - **Omgeving**: `test`
   - **Image tag**: `develop` (of een specifieke SHA)
4. Klik **Run workflow**

Na de deploy:
- Helm voert `migrate` uit als initContainer
- De `seed-data` Job laadt automatisch testdata (`seed_data --clear`)
- De applicatie is bereikbaar op https://test.softwarecatalogus.vngrealisatie.nl

### Testaccounts (na seed_data)

| Gebruiker | E-mail | Wachtwoord | Rol |
|-----------|--------|------------|-----|
| VNG Admin | admin@vngrealisatie.nl | Welkom01! | Functioneel beheerder |
| Utrecht | j.jansen@utrecht.nl | Welkom01! | Gebruik-beheerder |
| Centric | verkoop@centric.eu | Welkom01! | Aanbod-beheerder |

> Wachtwoord wijzigen na eerste login is verplicht.

---

## Testdata opnieuw laden

Om testdata te resetten zonder opnieuw te deployen:

```bash
kubectl create job seed-data-manual \
  --from=cronjob/softwarecatalogus-seed-data \
  -n softwarecatalogus-test

# Of direct via kubectl exec op een backend pod:
kubectl exec -n softwarecatalogus-test \
  deployment/softwarecatalogus-backend \
  -- python manage.py seed_data --clear
```

---

## Promotie tussen omgevingen

```
develop branch  →  Test omgeving     (automatisch na CI)
main branch     →  Acceptatie        (handmatig via workflow_dispatch)
main branch     →  Productie         (handmatig via workflow_dispatch, na acceptatie-goedkeuring)
```

Aanbevolen: stel **branch protection rules** in op `main` met verplichte review.
