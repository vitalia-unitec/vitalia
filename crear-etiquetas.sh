#!/usr/bin/env bash
# Crea las etiquetas del proyecto con GitHub CLI
# Uso: ./crear-etiquetas.sh usuario-u-organizacion/vitalia

REPO="$1"

gh label create backend          --repo "$REPO" --color 2E7D6B --description "Equipo de backend" --force
gh label create frontend         --repo "$REPO" --color 6BAF8F --description "Equipo de frontend" --force
gh label create base-de-datos    --repo "$REPO" --color D9B59F --description "Equipo de base de datos" --force
gh label create infraestructura  --repo "$REPO" --color 2D2D2D --description "Equipo de infraestructura" --force
gh label create tarea            --repo "$REPO" --color 0E8A16 --description "Algo que hay que hacer" --force
gh label create error            --repo "$REPO" --color D73A4A --description "Algo no funciona" --force
gh label create contrato         --repo "$REPO" --color 5319E7 --description "Cambio al contrato de la API" --force
gh label create duda             --repo "$REPO" --color FBCA04 --description "Pregunta entre equipos" --force
gh label create urgente          --repo "$REPO" --color B60205 --description "Bloquea a otro equipo" --force
