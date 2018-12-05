#!/usr/bin/env bash
cd ansible && ansible-playbook -K -i inventory/totd_bot.ini -e @vars/secrets.yml --vault-password-file ~/.totd_bot_vault_pass.txt main.yml
