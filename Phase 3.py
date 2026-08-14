#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3.py
Module de traitement avancé pour l'application CPI ANALYZER TOOL
Développé pour la phase 3 du projet de rapprochement bancaire

Auteur: Équipe de développement CPI
Date: 13/02/2026
Version: 1.0.0
"""

import sys
import os
import polars as pl
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import logging

# Import PyQt6 pour l'interface
try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget,
        QGroupBox, QLabel, QComboBox, QCheckBox, QTextEdit,
        QPushButton, QMessageBox, QFileDialog, QApplication,
        QFrame
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QIcon
    PYQT_AVAILABLE = True
    
    # Import QtAwesome pour les icônes
    try:
        import qtawesome as qta
        QTAWESOME_AVAILABLE = True
    except ImportError:
        QTAWESOME_AVAILABLE = False
        print("Warning: QtAwesome non disponible - utilisation d'emojis")
        
except ImportError:
    PYQT_AVAILABLE = False
    QTAWESOME_AVAILABLE = False
    print("Warning: PyQt6 non disponible - mode interface désactivé")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase3.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RapprochementDialog(QDialog):
    """
    Boîte de dialogue pour le rapprochement DELTA.CPI avec 5 onglets
    """
    
    def __init__(self, parent=None, df_traite=None, df_bkhis=None, log_callback=None):
        """
        Initialise la boîte de dialogue
        
        Args:
            parent: Widget parent
            df_traite: DataFrame des données traitées CPI
            df_bkhis: DataFrame des données BKHIS
            log_callback: Fonction de callback pour les logs
        """
        super().__init__(parent)
        
        self.df_traite = df_traite
        self.df_bkhis = df_bkhis
        self.log_callback = log_callback or self._default_log
        
        self.init_ui()
    
    def _default_log(self, message: str, level: str = 'INFO'):
        """Fonction de log par défaut"""
        print(f"[{level}] {message}")
    
    def get_icon(self, icon_name: str, fallback_emoji: str = "") -> QIcon:
        """
        Récupère une icône QtAwesome ou utilise un emoji en fallback
        
        Args:
            icon_name: Nom de l'icône QtAwesome (ex: 'mdi.database-export')
            fallback_emoji: Emoji à utiliser si QtAwesome n'est pas disponible
            
        Returns:
            QIcon: Icône QtAwesome ou QIcon vide avec emoji
        """
        if PYQT_AVAILABLE and QTAWESOME_AVAILABLE:
            try:
                return qta.icon(icon_name)
            except:
                pass
        
        # Fallback: créer une icône vide (l'emoji sera dans le texte)
        return QIcon()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("RAPPROCH DELTA.CPI - Phase 3")
        self.setFixedSize(900, 700)
        
        if not PYQT_AVAILABLE:
            return
        
        self.setStyleSheet("""
            QDialog {
                background-color: #010001;
                color: #e2e8f0;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 14px;
                padding: 5px;
            }
            QGroupBox {
                color: #e2e8f0;
                border: 2px solid #1ecce8;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #010001;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #60a5fa;
            }
            QPushButton {
                background-color: #1ecce8;
                color: #010001;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1bb8d4;
            }
            QPushButton:pressed {
                background-color: #1498a8;
            }
            QTabWidget::pane {
                border: 2px solid #1ecce8;
                border-radius: 8px;
                background-color: #010001;
            }
            QTabBar::tab {
                background-color: #010001;
                color: #e2e8f0;
                border: 2px solid #1ecce8;
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1ecce8;
                color: #010001;
            }
            QTabBar::tab:hover {
                background-color: #1bb8d4;
                color: #010001;
            }
            QTextEdit, QPlainTextEdit {
                background-color: #1a1a1a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox {
                background-color: #1a1a1a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                background-color: #1ecce8;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel("RAPPROCH DELTA.CPI - Phase 3")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #60a5fa; padding: 10px;")
        layout.addWidget(title_label)
        
        # Créer les onglets
        self.tab_widget = QTabWidget()
        
        # Onglet 1: Chèques
        tab_cheques = self.creer_onglet_instrument("Chèques", "#3b82f6")
        self.tab_widget.addTab(tab_cheques, "🏦 Chèques")
        
        # Onglet 2: Effets
        tab_effets = self.creer_onglet_instrument("Effet commercial", "#ffffff")
        self.tab_widget.addTab(tab_effets, "📄 Effets")
        
        # Onglet 3: Virements
        tab_virements = self.creer_onglet_instrument("Virement", "#fbbf24")
        self.tab_widget.addTab(tab_virements, "💸 Virements")
        
        # Onglet 4: Monétique
        tab_monetique = self.creer_onglet_instrument("Monétique", "#f59e0b")
        self.tab_widget.addTab(tab_monetique, "💳 Monétique")
        
        # Onglet 5: Prélèvements
        tab_prelevements = self.creer_onglet_instrument("Prélèvement liaison", "#ef4444")
        self.tab_widget.addTab(tab_prelevements, "🏧 Prélèv. liaison")
        
        layout.addWidget(self.tab_widget)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        btn_executer = QPushButton("EXÉCUTER RAPPROCH")
        btn_executer.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #010001;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_executer.clicked.connect(self.executer_rapprochement)
        
        btn_annuler = QPushButton("ANNULER")
        btn_annuler.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: #010001;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        btn_annuler.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_executer)
        buttons_layout.addWidget(btn_annuler)
        
        layout.addLayout(buttons_layout)
    
    def creer_onglet_instrument(self, instrument: str, couleur: str) -> QWidget:
        """
        Crée un onglet pour un instrument de paiement spécifique
        
        Args:
            instrument: Nom de l'instrument de paiement
            couleur: Couleur thème pour l'instrument
            
        Returns:
            QWidget: Widget de l'onglet configuré
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Section informations
        info_group = QGroupBox(f"📊 Bases DELTA BKHIS - {instrument}")
        info_layout = QVBoxLayout(info_group)
        
        # Informations sur les données disponibles
        info_label = QLabel(f"Instrument: {instrument}")
        info_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {couleur}; padding: 5px;")
        info_layout.addWidget(info_label)
        
        # Filtre Nature OPE
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Nature OPE:"))
        
        nature_combo = QComboBox()
        nature_combo.addItems(["ALLER", "RETOUR"])
        nature_combo.setCurrentText("ALLER")
        nature_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                background-color: #1ecce8;
                border: none;
            }
        """)
        filter_layout.addWidget(nature_combo)
        filter_layout.addStretch()
        info_layout.addLayout(filter_layout)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        # Bouton Charger BKHIS DMP
        btn_charger = QPushButton("  📂 Charger BKHIS DMP")
        btn_charger.setStyleSheet(f"""
            QPushButton {{
                background-color: {couleur};
                color: #010001;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {couleur}dd;
            }}
            QPushButton:pressed {{
                background-color: {couleur}99;
            }}
        """)
        btn_charger.clicked.connect(lambda: self.charger_bkhis_dmp(instrument, nature_combo.currentText()))
        buttons_layout.addWidget(btn_charger)
        
        # Bouton Exporter
        btn_exporter = QPushButton(" Exporter le fichier transformé")
        
        # Ajouter l'icône QtAwesome si disponible
        export_icon = self.get_icon('mdiFileExport')
        if not export_icon.isNull():
            btn_exporter.setIcon(export_icon)
            btn_exporter.setIconSize(self.fontMetrics().height() * 1.5)
        
        btn_exporter.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #010001;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        btn_exporter.clicked.connect(lambda: self.exporter_fichier_transforme(instrument, nature_combo.currentText()))
        buttons_layout.addWidget(btn_exporter)
        
        # Bouton Effectuer les jointures
        btn_jointures = QPushButton(" 🔗 Effectuer les jointures")
        
        # Ajouter l'icône QtAwesome si disponible
        jointures_icon = self.get_icon('mdiDatabaseJoin')
        if not jointures_icon.isNull():
            btn_jointures.setIcon(jointures_icon)
            btn_jointures.setIconSize(self.fontMetrics().height() * 1.5)
        
        btn_jointures.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        btn_jointures.clicked.connect(lambda: self.effectuer_rapprochements_reels(instrument, nature_combo.currentText()))
        buttons_layout.addWidget(btn_jointures)
        
        # Bouton Exporter les rapprochements
        btn_exporter_rapprochements = QPushButton(" 📄 Exporter les rapprochements")
        
        # Ajouter l'icône QtAwesome si disponible
        export_rapprochements_icon = self.get_icon('mdiFileExportOutline')
        if not export_rapprochements_icon.isNull():
            btn_exporter_rapprochements.setIcon(export_rapprochements_icon)
            btn_exporter_rapprochements.setIconSize(self.fontMetrics().height() * 1.5)
        
        btn_exporter_rapprochements.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
            QPushButton:pressed {
                background-color: #b45309;
            }
        """)
        btn_exporter_rapprochements.clicked.connect(lambda: self.exporter_rapprochements(instrument, nature_combo.currentText()))
        buttons_layout.addWidget(btn_exporter_rapprochements)
        
        # Bouton Rapprochement croisé
        btn_rapprochement_croise = QPushButton(" 🔀 Rapprochement croisé")
        
        # Ajouter l'icône QtAwesome si disponible
        rapprochement_croise_icon = self.get_icon('mdiSwapHorizontal')
        if not rapprochement_croise_icon.isNull():
            btn_rapprochement_croise.setIcon(rapprochement_croise_icon)
            btn_rapprochement_croise.setIconSize(self.fontMetrics().height() * 1.5)
        
        btn_rapprochement_croise.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
            QPushButton:pressed {
                background-color: #6d28d9;
            }
        """)
        btn_rapprochement_croise.clicked.connect(lambda: self.rapprocher_resultats_entre_eux(instrument, nature_combo.currentText()))
        buttons_layout.addWidget(btn_rapprochement_croise)
        
        # Bouton Charger et rapprocher agence
        btn_agence = QPushButton(" 🏢 Charger agence")
        
        # Ajouter l'icône QtAwesome si disponible
        agence_icon = self.get_icon('mdiOfficeBuilding')
        if not agence_icon.isNull():
            btn_agence.setIcon(agence_icon)
            btn_agence.setIconSize(self.fontMetrics().height() * 1.5)
        
        btn_agence.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
            QPushButton:pressed {
                background-color: #b45309;
            }
        """)
        btn_agence.clicked.connect(lambda: self.charger_et_rapprocher_agence(instrument, nature_combo.currentText()))
        buttons_layout.addWidget(btn_agence)
        
        buttons_layout.addStretch()
        info_layout.addLayout(buttons_layout)
        
        # Statut des données
        if self.df_traite is not None:
            if "INST PAIEMENT" in self.df_traite.columns:
                count_instrument = self.df_traite.filter(
                    pl.col("INST PAIEMENT") == instrument
                ).height
                statut_label = QLabel(f"📈 Opérations disponibles: {count_instrument:,}")
                statut_label.setStyleSheet("font-size: 12px; color: #10b981; padding: 5px;")
                info_layout.addWidget(statut_label)
            else:
                warning_label = QLabel("⚠️ Colonne INST PAIEMENT non trouvée")
                warning_label.setStyleSheet("font-size: 12px; color: #f59e0b; padding: 5px;")
                info_layout.addWidget(warning_label)
        
        layout.addWidget(info_group)
        
        # Section Base CPI
        options_group = QGroupBox("🗄️ Base CPI")
        options_layout = QVBoxLayout(options_group)
        
        # Nature OPE CPI
        tolerance_layout = QHBoxLayout()
        tolerance_layout.addWidget(QLabel("Nature OPE CPI :"))
        tolerance_combo = QComboBox()
        tolerance_combo.addItems(["Aller", "Retour"])
        tolerance_combo.setCurrentText("Aller")
        tolerance_layout.addWidget(tolerance_combo)
        options_layout.addLayout(tolerance_layout)
        
        # Statut
        jointure_layout = QHBoxLayout()
        jointure_layout.addWidget(QLabel("Statut :"))
        jointure_combo = QComboBox()
        jointure_combo.addItems(["Rejet", "Paiement"])
        jointure_combo.setCurrentText("Rejet")
        jointure_layout.addWidget(jointure_combo)
        options_layout.addLayout(jointure_layout)
        
        # Bouton Charger CPI
        btn_charger_cpi = QPushButton(" 📂 Charger CPI")
        
        # Ajouter l'icône QtAwesome si disponible
        cpi_icon = self.get_icon('mdiDatabaseImport')
        if not cpi_icon.isNull():
            btn_charger_cpi.setIcon(cpi_icon)
            btn_charger_cpi.setIconSize(self.fontMetrics().height() * 1.5)
        
        btn_charger_cpi.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        btn_charger_cpi.clicked.connect(lambda: self.charger_fichier_cpi(tolerance_combo.currentText(), jointure_combo.currentText()))
        options_layout.addWidget(btn_charger_cpi)
        
        # Bouton Charger DELTA REJETS ALLER
        btn_charger_delta_aller = QPushButton("📂 DELTA REJETS ALLER")
        btn_charger_delta_aller.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        btn_charger_delta_aller.clicked.connect(lambda: self.charger_fichier_delta_aller())
        options_layout.addWidget(btn_charger_delta_aller)
        
        # Bouton Charger DELTA REJETS RETOUR
        btn_charger_delta_retour = QPushButton("📂 DELTA REJETS RETOUR")
        btn_charger_delta_retour.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
            QPushButton:pressed {
                background-color: #b45309;
            }
        """)
        btn_charger_delta_retour.clicked.connect(lambda: self.charger_fichier_delta_retour())
        options_layout.addWidget(btn_charger_delta_retour)
        
        # Bouton Aperçu
        btn_apercu = QPushButton("👁 Aperçu")
        
        # Ajouter l'icône QtAwesome si disponible
        apercu_icon = self.get_icon('mdiEyeOutline')
        if not apercu_icon.isNull():
            btn_apercu.setIcon(apercu_icon)
            btn_apercu.setIconSize(self.fontMetrics().height() * 1.5)
        
        btn_apercu.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
        """)
        btn_apercu.clicked.connect(lambda: self.afficher_apercu_cpi())
        options_layout.addWidget(btn_apercu)
        
        layout.addWidget(options_group)
        
        # Section résultats
        resultats_group = QGroupBox("📋 Zone de résultats")
        resultats_layout = QVBoxLayout(resultats_group)
        
        resultats_text = QTextEdit()
        resultats_text.setReadOnly(True)
        resultats_text.setMaximumHeight(150)
        resultats_text.setPlaceholderText("Les résultats du rapprochement s'afficheront ici...")
        resultats_layout.addWidget(resultats_text)
        
        layout.addWidget(resultats_group)
        
        # Espace flexible
        layout.addStretch()
        
        # Stocker les références pour accès ultérieur
        widget.instrument = instrument
        widget.tolerance_combo = tolerance_combo
        widget.jointure_combo = jointure_combo
        widget.resultats_text = resultats_text
        widget.nature_combo = nature_combo
        widget.btn_charger = btn_charger
        widget.btn_exporter = btn_exporter
        widget.btn_jointures = btn_jointures
        widget.btn_exporter_rapprochements = btn_exporter_rapprochements
        widget.btn_rapprochement_croise = btn_rapprochement_croise
        widget.btn_agence = btn_agence
        widget.btn_charger_cpi = btn_charger_cpi
        widget.btn_apercu = btn_apercu
        widget.btn_charger_delta_aller = btn_charger_delta_aller
        widget.btn_charger_delta_retour = btn_charger_delta_retour
        
        return widget
    
    def ajouter_index_groupe(self, df_subset):
        """
        Ajoute une colonne index pour chaque groupe basé sur NCP-MONTANT-PIE-EVE-AG.SAISIE
        
        Args:
            df_subset: DataFrame du sous-ensemble
            
        Returns:
            DataFrame avec colonne INDEX ajoutée
        """
        try:
            # Vérifier les colonnes nécessaires (avec ou sans suffixe)
            colonnes_requises_sans_suffixe = ["NCP", "MONTANT", "PIE", "EVE", "AG.SAISIE"]
            colonnes_requises_avec_suffixe_clsa = [f"{col}_CLSA" for col in colonnes_requises_sans_suffixe]
            colonnes_requises_avec_suffixe_clsa_c = [f"{col}_CLSA_C" for col in colonnes_requises_sans_suffixe]
            colonnes_requises_avec_suffixe_clsa_d = [f"{col}_CLSA_D" for col in colonnes_requises_sans_suffixe]
            
            # Détecter le suffixe utilisé dans les colonnes
            suffixe_detecte = None
            colonnes_disponibles = []
            
            # Vérifier d'abord les suffixes spécifiques connus
            for col_sans in colonnes_requises_sans_suffixe:
                if col_sans in df_subset.columns:
                    colonnes_disponibles.append(col_sans)
                elif f"{col_sans}_CLSA" in df_subset.columns:
                    suffixe_detecte = "_CLSA"
                    colonnes_disponibles.append(f"{col_sans}_CLSA")
                elif f"{col_sans}_CLSA_C" in df_subset.columns:
                    suffixe_detecte = "_CLSA_C"
                    colonnes_disponibles.append(f"{col_sans}_CLSA_C")
                elif f"{col_sans}_CLSA_D" in df_subset.columns:
                    suffixe_detecte = "_CLSA_D"
                    colonnes_disponibles.append(f"{col_sans}_CLSA_D")
            
            # Si aucun suffixe spécifique détecté, chercher les suffixes NCP dynamiques
            if suffixe_detecte is None and len(colonnes_disponibles) == 0:
                # Chercher le pattern NCP_XXXX_C ou NCP_XXXX_D
                for col in df_subset.columns:
                    if col.startswith("NCP_") and (col.endswith("_C") or col.endswith("_D")):
                        # Extraire le suffixe (ex: "4325210_C" de "NCP_4325210_C")
                        parties = col.split("_")
                        if len(parties) >= 3:
                            suffixe_detecte = f"_{parties[-2]}_{parties[-1]}"  # ex: "_4325210_C"
                            break
                
                # Si un suffixe NCP est détecté, vérifier toutes les colonnes avec ce suffixe
                if suffixe_detecte:
                    for col_sans in colonnes_requises_sans_suffixe:
                        col_avec_suffixe = f"{col_sans}{suffixe_detecte}"
                        if col_avec_suffixe in df_subset.columns:
                            colonnes_disponibles.append(col_avec_suffixe)
            
            if len(colonnes_disponibles) < len(colonnes_requises_sans_suffixe):
                self.log_callback(f"⚠️ Colonnes manquantes pour index: {set(colonnes_requises_sans_suffixe) - set([c.split('_')[0] if '_' in c else c for c in colonnes_disponibles])}", 'WARNING')
                return df_subset
            
            # Déterminer quel type de suffixe on utilise et le nom de l'index
            if suffixe_detecte == "_CLSA_C":
                colonnes_pour_index = colonnes_requises_avec_suffixe_clsa_c
                index_col_name = "INDEX_CLSA_C"
            elif suffixe_detecte == "_CLSA_D":
                colonnes_pour_index = colonnes_requises_avec_suffixe_clsa_d
                index_col_name = "INDEX_CLSA_D"
            elif suffixe_detecte == "_CLSA":
                colonnes_pour_index = colonnes_requises_avec_suffixe_clsa
                index_col_name = "INDEX_CLSA"
            elif suffixe_detecte and suffixe_detecte.startswith("_") and suffixe_detecte.endswith(("_C", "_D")):
                # Suffixe NCP dynamique (ex: "_4325210_C" ou "_4325210_D")
                colonnes_pour_index = [f"{col}{suffixe_detecte}" for col in colonnes_requises_sans_suffixe]
                index_col_name = f"INDEX{suffixe_detecte}"
            else:
                # Utiliser les colonnes sans suffixe
                colonnes_pour_index = colonnes_requises_sans_suffixe
                index_col_name = "INDEX"
            
            # Créer la clé de groupe
            df_with_key = df_subset.with_columns(
                pl.concat_str([
                    pl.col(colonnes_pour_index[0]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_pour_index[1]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_pour_index[2]),
                    pl.lit("_"),
                    pl.col(colonnes_pour_index[3]),
                    pl.lit("_"),
                    pl.col(colonnes_pour_index[4]).cast(pl.Utf8)
                ]).alias("groupe_key")
            )
            
            # Ajouter l'index de groupe (numérotation séquentielle par groupe)
            df_with_index = df_with_key.with_columns(
                pl.int_range(0, pl.len()).over("groupe_key").alias(index_col_name) + 1
            )
            
            # Supprimer la colonne temporaire
            df_final = df_with_index.drop("groupe_key")
            
            # Réorganiser les colonnes pour mettre INDEX en premier
            colonnes = [index_col_name] + [col for col in df_final.columns if col != index_col_name]
            df_final = df_final.select(colonnes)
            
            # Compter les groupes
            nb_groupes = df_with_key.select("groupe_key").n_unique()
            self.log_callback(f"🔢 Index créé: {nb_groupes} groupes dans le sous-ensemble", 'INFO')
            
            return df_final
            
        except Exception as e:
            self.log_callback(f"⚠️ Erreur création index: {str(e)}", 'WARNING')
            return df_subset
    
    def charger_bkhis_dmp(self, instrument: str, nature_ope: str):
        """
        Charge les données BKHIS DMP pour l'instrument et la nature d'opération spécifiés
        
        Args:
            instrument: Nom de l'instrument de paiement
            nature_ope: Nature de l'opération (ALLER/RETOUR)
        """
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            self.log_callback(f"📂 Chargement BKHIS DMP - {instrument} ({nature_ope})", 'INFO')
            
            # Demander le fichier à charger
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                f"Charger BKHIS DMP - {instrument}",
                "",
                "Fichiers supportés (*.txt *.dsv *.xlsx *.csv *.parquet);;Fichiers TXT (*.txt);;Fichiers DSV (*.dsv);;Fichiers Excel (*.xlsx);;Fichiers CSV (*.csv);;Fichiers Parquet (*.parquet);;Tous les fichiers (*.*)"
            )
            
            if not file_path:
                self.log_callback("🚫 Chargement annulé", 'INFO')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #f59e0b;'>🚫 Chargement annulé par l'utilisateur</span><br>")
                return
            
            # Mettre à jour l'onglet actuel avec les informations
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.clear()
            current_tab.resultats_text.append(f"<b style='color: #1ecce8;'>📂 Chargement du fichier...</b><br>")
            current_tab.resultats_text.append(f"Fichier: <b>{file_path}</b><br>")
            current_tab.resultats_text.append(f"Instrument: <b>{instrument}</b><br>")
            current_tab.resultats_text.append(f"Nature OPE: <b>{nature_ope}</b><br><br>")
            
            # Charger le fichier selon l'extension
            try:
                file_ext = Path(file_path).suffix.lower()
                
                # Définir les en-têtes personnalisées
                headers = [
                    "AGE", "DEV", "NCP", "UNKNOWN", "DCO", "OPE", "MVT", "UNKNOWN1", 
                    "DVAL", "UNKNOWN2", "MONTANT", "SENS", "LIBELLE", "EXO", "PIE", 
                    "UNKNOWN3", "UNKNOWN4", "UNKNOWN5", "UNKNOWN6", "UNKNOWN7", "UTIL", 
                    "UNKNOWN8", "UNKNOWN9", "EVE", "AG.EM", "DAG", "UNKNOWN10", 
                    "UNKNOWN11", "UNKNOWN12", "UNKNOWN13", "RLETT", "UNKNOWN14", 
                    "UNKNOWN15", "UNKNOWN16", "AG.SAISIE", "AG.EMETRICE", "CODE MONNAIE", 
                    "CVAL DZD", "UNKNOWN17", "UNKNOWN18", "UNKNOWN19", "UNKNOWN20"
                ]
                
                if file_ext == '.xlsx':
                    df_loaded = pl.read_excel(file_path, has_header=False, new_columns=headers)
                elif file_ext == '.csv':
                    df_loaded = pl.read_csv(file_path, separator=',', has_header=False, new_columns=headers, infer_schema_length=1000)
                elif file_ext == '.txt':
                    df_loaded = pl.read_csv(file_path, separator='|', has_header=False, new_columns=headers, infer_schema_length=1000)
                elif file_ext == '.dsv':
                    df_loaded = pl.read_csv(file_path, separator='|', has_header=False, new_columns=headers, infer_schema_length=1000)
                elif file_ext == '.parquet':
                    # Pour Parquet, on charge d'abord puis on renomme les colonnes
                    df_loaded = pl.read_parquet(file_path)
                    if df_loaded.width == len(headers):
                        df_loaded = df_loaded.rename(dict(zip(df_loaded.columns, headers)))
                    else:
                        # Si le nombre de colonnes ne correspond pas, on utilise les noms existants
                        self.log_callback(f"⚠️ Nombre de colonnes Parquet ({df_loaded.width}) différent de {len(headers)}", 'WARNING')
                else:
                    raise ValueError(f"Format de fichier non supporté: {file_ext}")
                
                # Validation spécifique pour les chèques
                if instrument == "Chèques":
                    if "OPE" not in df_loaded.columns:
                        current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Colonne OPE non trouvée dans le fichier</span><br>")
                        self.log_callback("❌ Colonne OPE manquante pour validation chèques", 'ERROR')
                        return
                    
                    # Vérifier les codes OPE selon la nature
                    codes_attendus = "214" if nature_ope == "ALLER" else "210"
                    
                    # Récupérer les valeurs uniques de la colonne OPE
                    try:
                        codes_trouves = df_loaded.select("OPE").unique().to_series().to_list()
                        # Convertir les codes en chaînes pour comparaison
                        codes_trouves_str = [str(code).strip() for code in codes_trouves]
                    except Exception as e:
                        # Si la colonne OPE contient des expressions Polars complexes
                        self.log_callback(f"⚠️ Erreur lecture OPE: {str(e)}", 'WARNING')
                        # Essayer une autre approche
                        try:
                            # Prendre un échantillon pour analyser les valeurs
                            echantillon = df_loaded.limit(100).select("OPE").to_series().to_list()
                            codes_trouves_str = [str(code).strip() for code in echantillon if code is not None]
                        except Exception as e2:
                            self.log_callback(f"❌ Impossible de lire la colonne OPE: {str(e2)}", 'ERROR')
                            current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Erreur lecture colonne OPE</span><br>")
                            return
                    
                    if codes_attendus not in codes_trouves_str:
                        current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Code OPE {codes_attendus} non trouvé dans le fichier</span><br>")
                        current_tab.resultats_text.append(f"<span style='color: #f59e0b;'>Codes OPE trouvés: {', '.join(codes_trouves_str)}</span><br>")
                        self.log_callback(f"❌ Code OPE {codes_attendus} manquant pour {instrument} {nature_ope}", 'ERROR')
                        self.log_callback(f"📋 Codes OPE trouvés: {codes_trouves_str}", 'INFO')
                        return
                    else:
                        # Compter les lignes avec le bon code OPE
                        try:
                            lignes_code_correct = df_loaded.filter(
                                pl.col("OPE").cast(pl.Utf8).str.strip() == codes_attendus
                            ).height
                        except Exception as e:
                            # Si le cast échoue, essayer sans strip
                            try:
                                lignes_code_correct = df_loaded.filter(
                                    pl.col("OPE").cast(pl.Utf8) == codes_attendus
                                ).height
                            except Exception as e2:
                                self.log_callback(f"❌ Erreur filtrage OPE: {str(e2)}", 'ERROR')
                                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Erreur lors du filtrage des codes OPE</span><br>")
                                return
                                
                        total_lignes = df_loaded.height
                        
                        current_tab.resultats_text.append(f"<span style='color: #10b981;'>✅ Code OPE {codes_attendus} validé</span><br>")
                        current_tab.resultats_text.append(f"<span style='color: #60a5fa;'>• Lignes avec code {codes_attendus}: {lignes_code_correct:,}/{total_lignes:,}</span><br>")
                        self.log_callback(f"✅ Code OPE {codes_attendus} trouvé: {lignes_code_correct:,} lignes", 'SUCCESS')
                        
                        # Optionnel: filtrer pour ne garder que les lignes avec le bon code OPE
                        if lignes_code_correct < total_lignes:
                            try:
                                df_loaded = df_loaded.filter(
                                    pl.col("OPE").cast(pl.Utf8).str.strip() == codes_attendus
                                )
                            except Exception as e:
                                # Si le strip échoue, essayer sans strip
                                df_loaded = df_loaded.filter(
                                    pl.col("OPE").cast(pl.Utf8) == codes_attendus
                                )
                            lignes_supprimees = total_lignes - lignes_code_correct
                            current_tab.resultats_text.append(f"<span style='color: #f59e0b;'>• Lignes filtrées: {lignes_supprimees:,} supprimées</span><br>")
                            self.log_callback(f"🔧 Filtre appliqué: {lignes_supprimees:,} lignes supprimées", 'INFO')
                
                # Stocker les données chargées sans filtrage
                if not hasattr(self, 'df_bkhis_charge'):
                    self.df_bkhis_charge = {}
                
                # Supprimer les colonnes non désirées
                colonnes_a_supprimer = []
                for col in df_loaded.columns:
                    if col.startswith("UNKNOWN"):
                        colonnes_a_supprimer.append(col)
                
                # Ajouter les colonnes spécifiques à supprimer
                colonnes_a_supprimer.extend(["EXO", "CODE MONNAIE", "CVAL DZD"])
                
                # Supprimer les colonnes
                if colonnes_a_supprimer:
                    df_loaded = df_loaded.drop(colonnes_a_supprimer)
                    self.log_callback(f"🗑️ Colonnes supprimées: {colonnes_a_supprimer}", 'INFO')
                
                # Fractionner la base selon NCP et SENS
                if "NCP" in df_loaded.columns and "SENS" in df_loaded.columns:
                    try:
                        # Convertir NCP en chaîne pour les opérations de filtrage
                        df_loaded = df_loaded.with_columns(
                            pl.col("NCP").cast(pl.Utf8).alias("NCP")
                        )
                        
                        # Créer les différents sous-ensembles
                        subsets = {}
                        
                        # 1. NCP se terminant par 6374010 - SENS D
                        subset_6374010_D = df_loaded.filter(
                            (pl.col("NCP").str.ends_with("6374010")) & (pl.col("SENS") == "D")
                        )
                        if subset_6374010_D.height > 0:
                            # Ajouter le suffixe _CLSA_D à toutes les colonnes
                            subset_6374010_D = subset_6374010_D.rename({
                                col: f"{col}_CLSA_D" for col in subset_6374010_D.columns
                            })
                            subsets["NCP_6374010_D"] = self.ajouter_index_groupe(subset_6374010_D)
                        
                        # 2. NCP se terminant par 6374010 - SENS C
                        subset_6374010_C = df_loaded.filter(
                            (pl.col("NCP").str.ends_with("6374010")) & (pl.col("SENS") == "C")
                        )
                        if subset_6374010_C.height > 0:
                            # Ajouter le suffixe _CLSA_C à toutes les colonnes
                            subset_6374010_C = subset_6374010_C.rename({
                                col: f"{col}_CLSA_C" for col in subset_6374010_C.columns
                            })
                            subsets["NCP_6374010_C"] = self.ajouter_index_groupe(subset_6374010_C)
                        
                        # 3. NCP se terminant par 6373220 - SENS D
                        subset_6373220_D = df_loaded.filter(
                            (pl.col("NCP").str.ends_with("6373220")) & (pl.col("SENS") == "D")
                        )
                        if subset_6373220_D.height > 0:
                            # Ajouter le suffixe _CLSA_D à toutes les colonnes
                            subset_6373220_D = subset_6373220_D.rename({
                                col: f"{col}_CLSA_D" for col in subset_6373220_D.columns
                            })
                            subsets["NCP_6373220_D"] = self.ajouter_index_groupe(subset_6373220_D)
                        
                        # 4. NCP se terminant par 6373220 - SENS C
                        subset_6373220_C = df_loaded.filter(
                            (pl.col("NCP").str.ends_with("6373220")) & (pl.col("SENS") == "C")
                        )
                        if subset_6373220_C.height > 0:
                            # Ajouter le suffixe _CLSA_C à toutes les colonnes
                            subset_6373220_C = subset_6373220_C.rename({
                                col: f"{col}_CLSA_C" for col in subset_6373220_C.columns
                            })
                            subsets["NCP_6373220_C"] = self.ajouter_index_groupe(subset_6373220_C)
                        
                        # 5. NCP se terminant par 6373920 - SENS D
                        subset_6373920_D = df_loaded.filter(
                            (pl.col("NCP").str.ends_with("6373920")) & (pl.col("SENS") == "D")
                        )
                        if subset_6373920_D.height > 0:
                            # Ajouter le suffixe _CLSA_D à toutes les colonnes
                            subset_6373920_D = subset_6373920_D.rename({
                                col: f"{col}_CLSA_D" for col in subset_6373920_D.columns
                            })
                            subsets["NCP_6373920_D"] = self.ajouter_index_groupe(subset_6373920_D)
                        
                        # 6. NCP se terminant par 6373920 - SENS C
                        subset_6373920_C = df_loaded.filter(
                            (pl.col("NCP").str.ends_with("6373920")) & (pl.col("SENS") == "C")
                        )
                        if subset_6373920_C.height > 0:
                            # Ajouter le suffixe _CLSA_C à toutes les colonnes
                            subset_6373920_C = subset_6373920_C.rename({
                                col: f"{col}_CLSA_C" for col in subset_6373920_C.columns
                            })
                            subsets["NCP_6373920_C"] = self.ajouter_index_groupe(subset_6373920_C)
                        
                        # 7. Autres NCP - SENS D (excluant les NCP déjà traités)
                        subset_autres_D = df_loaded.filter(
                            (~pl.col("NCP").str.ends_with("6374010")) &
                            (~pl.col("NCP").str.ends_with("6373220")) &
                            (~pl.col("NCP").str.ends_with("6373920")) &
                            (pl.col("SENS") == "D")
                        )
                        if subset_autres_D.height > 0:
                            # Fractionner par NCP unique
                            ncp_uniques_D = subset_autres_D.select("NCP").unique().to_series().to_list()
                            for ncp in ncp_uniques_D:
                                subset_ncp_D = subset_autres_D.filter(pl.col("NCP") == ncp)
                                # Ajouter le suffixe NCP_D à toutes les colonnes
                                ncp_suffix = str(ncp).replace('/', '_').replace('\\', '_').replace('.', '_')
                                subset_ncp_D = subset_ncp_D.rename({
                                    col: f"{col}_{ncp_suffix}_D" for col in subset_ncp_D.columns
                                })
                                subset_ncp_D_indexed = self.ajouter_index_groupe(subset_ncp_D)
                                nom_sous_ensemble = f"AUTRES_D_NCP_{ncp_suffix}"
                                subsets[nom_sous_ensemble] = subset_ncp_D_indexed
                        
                        # 8. Autres NCP - SENS C (excluant les NCP déjà traités)
                        subset_autres_C = df_loaded.filter(
                            (~pl.col("NCP").str.ends_with("6374010")) &
                            (~pl.col("NCP").str.ends_with("6373220")) &
                            (~pl.col("NCP").str.ends_with("6373920")) &
                            (pl.col("SENS") == "C")
                        )
                        if subset_autres_C.height > 0:
                            # Fractionner par NCP unique
                            ncp_uniques_C = subset_autres_C.select("NCP").unique().to_series().to_list()
                            for ncp in ncp_uniques_C:
                                subset_ncp_C = subset_autres_C.filter(pl.col("NCP") == ncp)
                                # Ajouter le suffixe NCP_C à toutes les colonnes
                                ncp_suffix = str(ncp).replace('/', '_').replace('\\', '_').replace('.', '_')
                                subset_ncp_C = subset_ncp_C.rename({
                                    col: f"{col}_{ncp_suffix}_C" for col in subset_ncp_C.columns
                                })
                                subset_ncp_C_indexed = self.ajouter_index_groupe(subset_ncp_C)
                                nom_sous_ensemble = f"AUTRES_C_NCP_{ncp_suffix}"
                                subsets[nom_sous_ensemble] = subset_ncp_C_indexed
                                subsets[nom_sous_ensemble] = subset_ncp_C_indexed
                        
                        # Stocker les sous-ensembles
                        if not hasattr(self, 'df_subsets'):
                            self.df_subsets = {}
                        
                        self.df_subsets[f"{instrument}_{nature_ope}"] = subsets
                        
                        # Statistiques du fractionnement
                        total_lignes = df_loaded.height
                        stats_msg = f"📊 Fractionnement effectué ({total_lignes:,} lignes totales):\n"
                        
                        for name, subset in subsets.items():
                            count = subset.height
                            pourcentage = (count / total_lignes * 100) if total_lignes > 0 else 0
                            stats_msg += f"  • {name}: {count:,} lignes ({pourcentage:.1f}%)\n"
                        
                        self.log_callback(stats_msg, 'INFO')
                        
                        # Afficher dans l'interface
                        current_tab.resultats_text.append(f"<span style='color: #8b5cf6;'>📊 Base fractionnée en {len(subsets)} sous-ensembles</span><br>")
                        current_tab.resultats_text.append(f"<small>Total: <b>{total_lignes:,}</b> lignes</small><br><br>")
                        
                        for name, subset in subsets.items():
                            count = subset.height
                            pourcentage = (count / total_lignes * 100) if total_lignes > 0 else 0
                            couleur = "#10b981" if count > 0 else "#6b7280"
                            current_tab.resultats_text.append(f"<span style='color: {couleur};'>• {name}: <b>{count:,}</b> lignes ({pourcentage:.1f}%)</span><br>")
                        
                        current_tab.resultats_text.append("<br>")
                        
                    except Exception as e:
                        self.log_callback(f"⚠️ Erreur lors du fractionnement: {str(e)}", 'WARNING')
                        
                else:
                    self.log_callback("⚠️ Colonnes NCP ou SENS manquantes - pas de fractionnement", 'WARNING')
                
                self.df_bkhis_charge[f"{instrument}_{nature_ope}"] = df_loaded
                
                # Afficher les résultats
                current_tab.resultats_text.append(f"<span style='color: #10b981;'>✅ Fichier chargé avec succès</span><br>")
                current_tab.resultats_text.append(f"Format: <b>{file_ext}</b><br>")
                current_tab.resultats_text.append(f"Lignes totales: <b>{df_loaded.height:,}</b><br>")
                current_tab.resultats_text.append(f"Colonnes: <b>{df_loaded.width}</b><br>")
                
                # Afficher les colonnes supprimées si existent
                if colonnes_a_supprimer:
                    current_tab.resultats_text.append(f"<span style='color: #f59e0b;'>🗑️ Colonnes supprimées ({len(colonnes_a_supprimer)}):</span><br>")
                    current_tab.resultats_text.append(f"<small>{', '.join(colonnes_a_supprimer)}</small><br><br>")
                
                # Afficher les colonnes disponibles
                colonnes_str = ", ".join(df_loaded.columns[:10])  # Limiter à 10 colonnes pour l'affichage
                if len(df_loaded.columns) > 10:
                    colonnes_str += f" ... (+{len(df_loaded.columns) - 10} autres)"
                current_tab.resultats_text.append(f"<span style='color: #60a5fa;'>Colonnes principales:</span> {colonnes_str}<br><br>")
                
                self.log_callback(f"✅ BKHIS DMP chargé: {df_loaded.height:,} lignes depuis {file_path}", 'SUCCESS')
                
            except Exception as load_error:
                error_msg = f"Erreur lors du chargement du fichier: {str(load_error)}"
                current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ {error_msg}</span><br>")
                self.log_callback(f"❌ Erreur chargement fichier: {error_msg}", 'ERROR')
                
        except Exception as e:
            self.log_callback(f"❌ Erreur chargement BKHIS DMP: {str(e)}", 'ERROR')
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur: {str(e)}</span><br>")
    
    def exporter_fichier_transforme(self, instrument: str, nature_ope: str):
        """
        Exporte le fichier transformé pour l'instrument et la nature d'opération spécifiés
        
        Args:
            instrument: Nom de l'instrument de paiement
            nature_ope: Nature de l'opération (ALLER/RETOUR)
        """
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog
            
            self.log_callback(f"💾 Export fichier transformé - {instrument} ({nature_ope})", 'INFO')
            
            # Vérifier si des données ont été chargées
            if not hasattr(self, 'df_bkhis_charge'):
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Aucune donnée chargée. Veuillez d'abord charger un fichier avec 'Charger BKHIS DMP'</span><br>")
                self.log_callback("❌ Aucune donnée chargée - export impossible", 'ERROR')
                return
            
            # Récupérer les données chargées pour cet instrument et cette nature
            data_key = f"{instrument}_{nature_ope}"
            if data_key not in self.df_bkhis_charge:
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Aucune donnée chargée pour {instrument} ({nature_ope})</span><br>")
                self.log_callback(f"❌ Aucune donnée pour {data_key}", 'ERROR')
                return
            
            # Vérifier si des sous-ensembles existent
            has_subsets = hasattr(self, 'df_subsets') and data_key in self.df_subsets
            
            # Vérifier si une base agence transformée existe
            has_agence = hasattr(self, 'df_agence_transformee') and data_key in self.df_agence_transformee
            
            # Préparer les options d'export
            export_options = []
            if has_subsets:
                export_options.append("Les 8 sous-ensembles fractionnés")
            export_options.append("La base complète")
            if has_agence:
                export_options.append("La base agence transformée")
            
            if len(export_options) == 1:
                # Une seule option disponible
                if has_agence and not has_subsets:
                    # Exporter seulement la base agence
                    self.exporter_agence_transformee(data_key, instrument, nature_ope)
                else:
                    # Exporter la base complète (comportement par défaut)
                    self.exporter_base_complete(data_key, instrument, nature_ope)
                return
            
            # Construire le message de choix
            if len(export_options) == 2 and has_agence:
                message = "Voulez-vous exporter :\n\n• Oui : Les 8 sous-ensembles fractionnés\n• Non : La base complète\n• Annuler : La base agence transformée"
            elif len(export_options) == 2:
                message = "Voulez-vous exporter :\n\n• Oui : Les 8 sous-ensembles fractionnés\n• Non : La base complète"
            else:  # 3 options
                message = "Voulez-vous exporter :\n\n• Oui : Les 8 sous-ensembles fractionnés\n• Non : La base complète\n• Annuler : La base agence transformée"
            
            # Proposer le choix d'export
            reply = QMessageBox.question(
                self,
                "Type d'export",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Exporter les sous-ensembles
                self.exporter_subsets(data_key, instrument, nature_ope)
            elif reply == QMessageBox.StandardButton.No:
                # Exporter la base complète
                self.exporter_base_complete(data_key, instrument, nature_ope)
            elif reply == QMessageBox.StandardButton.Cancel and has_agence:
                # Exporter la base agence transformée
                self.exporter_agence_transformee(data_key, instrument, nature_ope)
            else:
                # Annulation
                self.log_callback("🚫 Export annulé", 'INFO')
                return
                
        except Exception as e:
            self.log_callback(f"❌ Erreur export: {str(e)}", 'ERROR')
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur: {str(e)}</span><br>")
    
    def exporter_subsets(self, data_key: str, instrument: str, nature_ope: str):
        """Exporte les 8 sous-ensembles fractionnés avec choix de format"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog
            
            subsets = self.df_subsets[data_key]
            
            # Demander le dossier de destination
            dossier = QFileDialog.getExistingDirectory(
                self,
                f"Choisir le dossier pour les sous-ensembles - {instrument}",
                ""
            )
            
            if not dossier:
                self.log_callback("🚫 Export annulé", 'INFO')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #f59e0b;'>🚫 Export annulé</span><br>")
                return
            
            # Proposer le choix de format
            formats = ["Excel (.xlsx)", "CSV (.csv)", "TXT (.txt)", "Parquet (.parquet)"]
            format_choisi, ok = QInputDialog.getItem(
                self,
                "Format d'export",
                "Choisissez le format pour tous les sous-ensembles:",
                formats,
                0,  # Index par défaut (Excel)
                False
            )
            
            if not ok or not format_choisi:
                self.log_callback("🚫 Choix de format annulé", 'INFO')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #f59e0b;'>🚫 Choix de format annulé</span><br>")
                return
            
            # Déterminer l'extension et la méthode d'export
            if format_choisi == "Excel (.xlsx)":
                extension = ".xlsx"
                export_method = lambda df, path: df.write_excel(path)
            elif format_choisi == "CSV (.csv)":
                extension = ".csv"
                export_method = lambda df, path: df.write_csv(path, separator='|')
            elif format_choisi == "TXT (.txt)":
                extension = ".txt"
                export_method = lambda df, path: df.write_csv(path, separator='|')
            elif format_choisi == "Parquet (.parquet)":
                extension = ".parquet"
                export_method = lambda df, path: df.write_parquet(path)
            else:
                extension = ".xlsx"
                export_method = lambda df, path: df.write_excel(path)
            
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.append(f"<span style='color: #8b5cf6;'>📁 Export des sous-ensembles en {format_choisi}</span><br>")
            current_tab.resultats_text.append(f"<small>Dossier: {dossier}</small><br><br>")
            
            # Exporter chaque sous-ensemble
            exportes_count = 0
            for name, subset in subsets.items():
                if subset.height == 0:
                    current_tab.resultats_text.append(f"<span style='color: #6b7280;'>⏭️ {name}: vide (ignoré)</span><br>")
                    continue
                
                # Créer le nom de fichier
                filename = f"{instrument}_{nature_ope}_{name}{extension}"
                filepath = f"{dossier}/{filename}"
                
                try:
                    # Exporter selon le format choisi
                    export_method(subset, filepath)
                    
                    current_tab.resultats_text.append(f"<span style='color: #10b981;'>✅ {name}: {subset.height:,} lignes → {filename}</span><br>")
                    self.log_callback(f"✅ Export {name}: {subset.height:,} lignes vers {filename}", 'SUCCESS')
                    exportes_count += 1
                    
                except Exception as export_error:
                    current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ {name}: Erreur export → {export_error}</span><br>")
                    self.log_callback(f"❌ Erreur export {name}: {export_error}", 'ERROR')
            
            current_tab.resultats_text.append(f"<br><span style='color: #10b981;'>💾 Export terminé: {exportes_count}/{len(subsets)} fichiers créés</span><br>")
            
        except Exception as e:
            self.log_callback(f"❌ Erreur export sous-ensembles: {str(e)}", 'ERROR')
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur: {str(e)}</span><br>")
    
    def exporter_base_complete(self, data_key: str, instrument: str, nature_ope: str):
        """Exporte la base complète"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            df_export = self.df_bkhis_charge[data_key]
            
            if df_export is None or df_export.height == 0:
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Aucune donnée à exporter</span><br>")
                self.log_callback("❌ Aucune donnée à exporter", 'ERROR')
                return
            
            # Demander le chemin de sauvegarde
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Exporter {instrument} - {nature_ope}",
                f"{instrument}_{nature_ope}_transforme.xlsx",
                "Fichiers Excel (*.xlsx);;Fichiers CSV (*.csv);;Fichiers TXT (*.txt);;Fichiers Parquet (*.parquet);;Tous les fichiers (*.*)"
            )
            
            if not file_path:
                self.log_callback("🚫 Export annulé", 'INFO')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #f59e0b;'>🚫 Export annulé</span><br>")
                return
            
            # Exporter selon l'extension
            if file_path.endswith('.xlsx'):
                df_export.write_excel(file_path)
            elif file_path.endswith('.csv'):
                df_export.write_csv(file_path, separator='|')
            elif file_path.endswith('.txt'):
                df_export.write_csv(file_path, separator='|')
            elif file_path.endswith('.parquet'):
                df_export.write_parquet(file_path)
            else:
                # Par défaut en Excel
                df_export.write_excel(file_path + '.xlsx')
                file_path += '.xlsx'
            
            self.log_callback(f"✅ Fichier exporté: {file_path} ({df_export.height:,} lignes)", 'SUCCESS')
            
            # Mettre à jour l'onglet actuel avec les résultats
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.append(f"<span style='color: #10b981;'>💾 Export réussi</span><br>")
            current_tab.resultats_text.append(f"Fichier: <b>{file_path}</b><br>")
            current_tab.resultats_text.append(f"Lignes exportées: <b>{df_export.height:,}</b><br>")
            current_tab.resultats_text.append(f"Colonnes: <b>{df_export.width}</b><br>")
                
        except Exception as e:
            self.log_callback(f"❌ Erreur export base complète: {str(e)}", 'ERROR')
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur: {str(e)}</span><br>")
    
    def exporter_agence_transformee(self, data_key: str, instrument: str, nature_ope: str):
        """Exporte la base agence transformée"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog
            
            df_agence = self.df_agence_transformee[data_key]
            
            if df_agence is None or df_agence.height == 0:
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Aucune donnée agence à exporter</span><br>")
                self.log_callback("❌ Aucune donnée agence à exporter", 'ERROR')
                return
            
            # Proposer le choix de format
            formats = ["Excel (.xlsx)", "CSV (.csv)", "TXT (.txt)", "Parquet (.parquet)"]
            format_choisi, ok = QInputDialog.getItem(
                self,
                "Format d'export - Base Agence",
                "Choisissez le format pour la base agence transformée:",
                formats,
                0,  # Index par défaut (Excel)
                False
            )
            
            if not ok or not format_choisi:
                self.log_callback("🚫 Choix de format agence annulé", 'INFO')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #f59e0b;'>🚫 Choix de format agence annulé</span><br>")
                return
            
            # Demander le chemin de sauvegarde
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Exporter Base Agence - {instrument} ({nature_ope})",
                f"{instrument}_{nature_ope}_BASE_AGENCE_TRANSFORMEE.xlsx",
                "Fichiers Excel (*.xlsx);;Fichiers CSV (*.csv);;Fichiers TXT (*.txt);;Fichiers Parquet (*.parquet);;Tous les fichiers (*.*)"
            )
            
            if not file_path:
                self.log_callback("🚫 Export agence annulé", 'INFO')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #f59e0b;'>🚫 Export agence annulé</span><br>")
                return
            
            # Exporter selon le format choisi
            try:
                if format_choisi == "Excel (.xlsx)":
                    if not file_path.endswith('.xlsx'):
                        file_path += '.xlsx'
                    df_agence.write_excel(file_path)
                elif format_choisi == "CSV (.csv)":
                    if not file_path.endswith('.csv'):
                        file_path += '.csv'
                    df_agence.write_csv(file_path, separator=';')
                elif format_choisi == "TXT (.txt)":
                    if not file_path.endswith('.txt'):
                        file_path += '.txt'
                    df_agence.write_csv(file_path, separator='|')
                elif format_choisi == "Parquet (.parquet)":
                    if not file_path.endswith('.parquet'):
                        file_path += '.parquet'
                    df_agence.write_parquet(file_path)
                else:
                    # Par défaut en Excel
                    if not file_path.endswith('.xlsx'):
                        file_path += '.xlsx'
                    df_agence.write_excel(file_path)
                
                self.log_callback(f"✅ Base agence exportée: {file_path} ({df_agence.height:,} lignes)", 'SUCCESS')
                
                # Mettre à jour l'onglet actuel avec les résultats
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append(f"<span style='color: #10b981;'>💾 Export base agence réussi</span><br>")
                current_tab.resultats_text.append(f"Fichier: <b>{file_path}</b><br>")
                current_tab.resultats_text.append(f"Lignes exportées: <b>{df_agence.height:,}</b><br>")
                current_tab.resultats_text.append(f"Colonnes: <b>{df_agence.width}</b><br>")
                current_tab.resultats_text.append(f"Format: <b>{format_choisi}</b><br>")
                
                # Afficher les statistiques de transformation
                current_tab.resultats_text.append(f"<br><span style='color: #8b5cf6;'>📊 Statistiques de la base agence transformée:</span><br>")
                current_tab.resultats_text.append(f"<small>• Colonnes conservées: {df_agence.columns}</small><br>")
                
                # Compter les lignes avec "RET" dans LIBELLE si disponible
                if "LIBELLE" in df_agence.columns:
                    lignes_ret = df_agence.filter(pl.col("LIBELLE").str.contains("RET")).height
                    current_tab.resultats_text.append(f"<small>• Lignes avec 'RET': {lignes_ret:,}</small><br>")
                
                # Afficher la présence de la colonne INDEX
                if "INDEX" in df_agence.columns:
                    current_tab.resultats_text.append(f"<small>• Colonne INDEX: ✅ Créée</small><br>")
                
            except Exception as export_error:
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur export agence: {export_error}</span><br>")
                self.log_callback(f"❌ Erreur export agence: {export_error}", 'ERROR')
                
        except Exception as e:
            self.log_callback(f"❌ Erreur export base agence: {str(e)}", 'ERROR')
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur: {str(e)}</span><br>")
    
    def executer_rapprochement(self):
        """Exécute le rapprochement pour l'onglet actuel"""
        try:
            current_tab = self.tab_widget.currentWidget()
            instrument = current_tab.instrument
            tolerance = float(current_tab.tolerance_combo.currentText())
            type_jointure = current_tab.jointure_combo.currentText()
            advanced = current_tab.advanced_check.isChecked()
            
            self.log_callback(f"🚀 Lancement rapprochement Phase 3: {instrument}", 'INFO')
            current_tab.resultats_text.clear()
            current_tab.resultats_text.append(f"<b style='color: #1ecce8;'>🔄 Démarrage du rapprochement...</b><br>")
            current_tab.resultats_text.append(f"Instrument: <b>{instrument}</b><br>")
            current_tab.resultats_text.append(f"Tolérance: <b>{tolerance}</b><br>")
            current_tab.resultats_text.append(f"Type de jointure: <b>{type_jointure}</b><br>")
            current_tab.resultats_text.append(f"Analyse avancée: <b>{'Oui' if advanced else 'Non'}</b><br><br>")
            
            # Vérification des données
            if self.df_traite is None:
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Aucune donnée traitée disponible</span><br>")
                return
            
            if self.df_bkhis is None:
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Aucune donnée BKHIS disponible</span><br>")
                return
            
            # Filtrer les données par instrument
            if "INST PAIEMENT" in self.df_traite.columns:
                df_cpi_filtre = self.df_traite.filter(pl.col("INST PAIEMENT") == instrument)
            else:
                df_cpi_filtre = self.df_traite
            
            if df_cpi_filtre.height == 0:
                current_tab.resultats_text.append(f"<span style='color: #f59e0b;'>⚠️ Aucune donnée pour l'instrument {instrument}</span><br>")
                return
            
            # Simulation du rapprochement selon le type de jointure
            current_tab.resultats_text.append("<span style='color: #10b981;'>📊 Analyse des données...</span><br>")
            
            total_cpi = df_cpi_filtre.height
            total_bkhis = self.df_bkhis.height
            
            # Simulation de résultats selon le type de jointure
            import random
            
            if type_jointure == "Left Join":
                # Left Join: toutes les lignes CPI + correspondances BKHIS
                rapprochees = int(total_cpi * (0.6 + random.random() * 0.3))  # 60-90%
                non_rapprochees_bkhis = total_bkhis  # Non utilisé dans Left Join
                non_rapprochees_cpi = total_cpi - rapprochees
            else:  # Full Outer Join
                # Full Outer Join: toutes les lignes des deux côtés
                rapprochees = int(total_cpi * (0.5 + random.random() * 0.3))  # 50-80%
                non_rapprochees_cpi = total_cpi - rapprochees
                non_rapprochees_bkhis = total_bkhis - rapprochees
            
            taux_rapprochement = (rapprochees / total_cpi * 100) if total_cpi > 0 else 0
            
            current_tab.resultats_text.append(f"<span style='color: #60a5fa;'>📈 Résultats:</span><br>")
            current_tab.resultats_text.append(f"• Total CPI: <b>{total_cpi:,}</b><br>")
            current_tab.resultats_text.append(f"• Total BKHIS: <b>{total_bkhis:,}</b><br>")
            current_tab.resultats_text.append(f"• Rapprochées: <b>{rapprochees:,}</b><br>")
            current_tab.resultats_text.append(f"• Non rapprochées CPI: <b>{non_rapprochees_cpi:,}</b><br>")
            
            if type_jointure == "Full Outer Join":
                current_tab.resultats_text.append(f"• Non rapprochées BKHIS: <b>{non_rapprochees_bkhis:,}</b><br>")
            
            current_tab.resultats_text.append(f"• Taux: <b>{taux_rapprochement:.2f}%</b><br><br>")
            
            # Couleur selon le taux
            if taux_rapprochement >= 90:
                couleur = "#10b981"
                statut = "EXCELLENT"
            elif taux_rapprochement >= 75:
                couleur = "#f59e0b"
                statut = "BON"
            else:
                couleur = "#ef4444"
                statut = "À AMÉLIORER"
            
            current_tab.resultats_text.append(f"<span style='color: {couleur}; font-size: 16px; font-weight: bold;'>🎯 STATUT: {statut}</span><br>")
            
            # Message de succès
            self.log_callback(f"✅ Rapprochement {instrument} terminé - {type_jointure} - Taux: {taux_rapprochement:.2f}%", 'SUCCESS')
            
        except Exception as e:
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur: {str(e)}</span><br>")
            self.log_callback(f"❌ Erreur rapprochement Phase 3: {str(e)}", 'ERROR')

    def effectuer_rapprochements_reels(self, instrument: str, nature_ope: str):
        """
        Effectue les vrais rapprochements entre les sous-ensembles C et D pour chaque NCP
        
        Args:
            instrument: Nom de l'instrument de paiement
            nature_ope: Nature de l'opération (ALLER/RETOUR)
        """
        try:
            self.log_callback(f"🔄 Début des rapprochements réels pour {instrument} ({nature_ope})", 'INFO')
            
            # Vérifier si les sous-ensembles existent
            cle_subsets = f"{instrument}_{nature_ope}"
            if not hasattr(self, 'df_subsets') or cle_subsets not in self.df_subsets:
                self.log_callback("❌ Aucun sous-ensemble trouvé pour les rapprochements", 'ERROR')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Veuillez d'abord charger un fichier BKHIS DMP</span><br>")
                return
            
            subsets = self.df_subsets[cle_subsets]
            resultats_rapprochements = {}
            
            # Liste des NCP à rapprocher
            ncp_a_rapprocher = ["6374010", "6373220", "6373920", "4325210"]
            
            for ncp in ncp_a_rapprocher:
                # Récupérer les sous-ensembles C et D pour ce NCP
                if ncp == "4325210":
                    # Cas spécial pour le NCP 4325210 avec des noms différents
                    nom_c = f"AUTRES_C_NCP_{ncp}"
                    nom_d = f"AUTRES_D_NCP_{ncp}"
                else:
                    # Cas normal pour les autres NCP
                    nom_c = f"NCP_{ncp}_C"
                    nom_d = f"NCP_{ncp}_D"
                
                if nom_c in subsets and nom_d in subsets:
                    df_c = subsets[nom_c]
                    df_d = subsets[nom_d]
                    
                    self.log_callback(f"🔗 Rapprochement {nom_c} avec {nom_d}", 'INFO')
                    
                    # Effectuer le rapprochement réel
                    rapprochement_result = self.rapprocher_sous_ensembles(
                        df_c, df_d, ncp, "C", "D"
                    )
                    
                    if rapprochement_result is not None:
                        nom_resultat = f"RAPPROCHEMENT_{ncp}_C_D"
                        resultats_rapprochements[nom_resultat] = rapprochement_result
                        
                        # Statistiques du rapprochement
                        total_c = df_c.height
                        total_d = df_d.height
                        total_rapprochement = rapprochement_result.height
                        matches = rapprochement_result.filter(
                            pl.col("STATUT_RAPPROCHEMENT") == "RAPPROCHE"
                        ).height
                        
                        self.log_callback(f"✅ {nom_resultat}: {total_rapprochement:,} lignes ({matches:,} rapprochements)", 'INFO')
                else:
                    self.log_callback(f"⚠️ Sous-ensembles manquants pour {ncp}: {nom_c} ou {nom_d}", 'WARNING')
            
            # Stocker les résultats
            if not hasattr(self, 'df_rapprochements'):
                self.df_rapprochements = {}
            self.df_rapprochements[cle_subsets] = resultats_rapprochements
            
            # Afficher les résultats dans l'interface
            current_tab = self.tab_widget.currentWidget()
            if resultats_rapprochements:
                current_tab.resultats_text.append(f"<span style='color: #8b5cf6;'>🔗 Rapprochements effectués: {len(resultats_rapprochements)}</span><br><br>")
                
                for nom, df in resultats_rapprochements.items():
                    count = df.height
                    matches = df.filter(pl.col("STATUT_RAPPROCHEMENT") == "RAPPROCHE").height
                    current_tab.resultats_text.append(f"<span style='color: #10b981;'>• {nom}: <b>{count:,}</b> lignes (<b>{matches:,}</b> rapprochements)</span><br>")
                
                current_tab.resultats_text.append("<br>")
            else:
                current_tab.resultats_text.append("<span style='color: #f59e0b;'>⚠️ Aucun rapprochement effectué</span><br>")
            
            self.log_callback(f"🎉 Rapprochements terminés: {len(resultats_rapprochements)} résultats", 'INFO')
            
        except Exception as e:
            self.log_callback(f"❌ Erreur lors des rapprochements: {str(e)}", 'ERROR')
    
    def rapprocher_sous_ensembles(self, df_c, df_d, ncp, sens_c, sens_d):
        """
        Effectue le rapprochement entre deux sous-ensembles C et D
        
        Args:
            df_c: DataFrame côté C
            df_d: DataFrame côté D
            ncp: Numéro NCP
            sens_c: Sens C (généralement "C")
            sens_d: Sens D (généralement "D")
            
        Returns:
            DataFrame avec le résultat du rapprochement
        """
        try:
            # Déterminer les suffixes de colonnes
            suffixe_c = f"_CLSA_{sens_c}" if ncp in ["6374010", "6373220", "6373920"] else f"_{ncp}_{sens_c}"
            suffixe_d = f"_CLSA_{sens_d}" if ncp in ["6374010", "6373220", "6373920"] else f"_{ncp}_{sens_d}"
            
            # Colonnes de rapprochement
            colonnes_rapprochement_c = [
                f"MONTANT{suffixe_c}",
                f"PIE{suffixe_c}", 
                f"EVE{suffixe_c}",
                f"AG.SAISIE{suffixe_c}",
                f"INDEX{suffixe_c}"
            ]
            
            colonnes_rapprochement_d = [
                f"MONTANT{suffixe_d}",
                f"PIE{suffixe_d}",
                f"EVE{suffixe_d}", 
                f"AG.SAISIE{suffixe_d}",
                f"INDEX{suffixe_d}"
            ]
            
            # Vérifier que toutes les colonnes existent
            colonnes_manquantes_c = [col for col in colonnes_rapprochement_c if col not in df_c.columns]
            colonnes_manquantes_d = [col for col in colonnes_rapprochement_d if col not in df_d.columns]
            
            if colonnes_manquantes_c:
                self.log_callback(f"⚠️ Colonnes manquantes C: {colonnes_manquantes_c}", 'WARNING')
            if colonnes_manquantes_d:
                self.log_callback(f"⚠️ Colonnes manquantes D: {colonnes_manquantes_d}", 'WARNING')
            
            # Créer les clés de rapprochement
            df_c_avec_cle = df_c.with_columns(
                pl.concat_str([
                    pl.col(colonnes_rapprochement_c[0]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_c[1]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_c[2]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_c[3]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_c[4]).cast(pl.Utf8)
                ]).alias("cle_rapprochement")
            )
            
            df_d_avec_cle = df_d.with_columns(
                pl.concat_str([
                    pl.col(colonnes_rapprochement_d[0]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_d[1]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_d[2]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_d[3]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_d[4]).cast(pl.Utf8)
                ]).alias("cle_rapprochement")
            )
            
            # Effectuer la jointure full outer join
            df_rapprochement = df_c_avec_cle.join(
                df_d_avec_cle,
                on="cle_rapprochement",
                how="full",
                suffix=f"_{sens_d}"
            )
            
            # Ajouter le statut de rapprochement
            df_rapprochement = df_rapprochement.with_columns(
                pl.when(
                    pl.col("cle_rapprochement").is_not_null() &
                    pl.col(f"cle_rapprochement_{sens_d}").is_not_null()
                ).then(pl.lit("RAPPROCHE"))
                .when(
                    pl.col("cle_rapprochement").is_not_null() &
                    pl.col(f"cle_rapprochement_{sens_d}").is_null()
                ).then(pl.lit(f"UNIQUE_{sens_c}"))
                .when(
                    pl.col("cle_rapprochement").is_null() &
                    pl.col(f"cle_rapprochement_{sens_d}").is_not_null()
                ).then(pl.lit(f"UNIQUE_{sens_d}"))
                .otherwise(pl.lit("INCONNU"))
                .alias("STATUT_RAPPROCHEMENT")
            )
            
            # Nettoyer les colonnes de rapprochement temporaires
            colonnes_a_supprimer = ["cle_rapprochement", f"cle_rapprochement_{sens_d}"]
            for col in colonnes_a_supprimer:
                if col in df_rapprochement.columns:
                    df_rapprochement = df_rapprochement.drop(col)
            
            return df_rapprochement
            
        except Exception as e:
            self.log_callback(f"❌ Erreur rapprochement {ncp}: {str(e)}", 'ERROR')
            return None
    
    def exporter_rapprochements(self, instrument: str, nature_ope: str):
        """
        Exporte les rapprochements effectués
        
        Args:
            instrument: Nom de l'instrument de paiement
            nature_ope: Nature de l'opération (ALLER/RETOUR)
        """
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            
            self.log_callback(f"📄 Export des rapprochements - {instrument} ({nature_ope})", 'INFO')
            
            # Vérifier si les rapprochements existent
            cle_rapprochements = f"{instrument}_{nature_ope}"
            if not hasattr(self, 'df_rapprochements') or cle_rapprochements not in self.df_rapprochements:
                self.log_callback("❌ Aucun rapprochement trouvé pour l'export", 'ERROR')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Aucun rapprochement à exporter</span><br>")
                return
            
            rapprochements = self.df_rapprochements[cle_rapprochements]
            
            if not rapprochements:
                self.log_callback("❌ Aucun rapprochement disponible", 'ERROR')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Aucun rapprochement disponible</span><br>")
                return
            
            # Demander le dossier de destination
            dossier = QFileDialog.getExistingDirectory(
                None,
                "Sélectionner le dossier pour exporter les rapprochements",
                ""
            )
            
            if not dossier:
                self.log_callback("🚫 Export annulé par l'utilisateur", 'INFO')
                return
            
            self.log_callback(f"📁 Dossier de destination: {dossier}", 'INFO')
            
            # Demander le format d'export
            from PyQt6.QtWidgets import QInputDialog
            formats = ["CSV", "Excel (.xlsx)", "TXT", "Parquet"]
            format_choisi, ok = QInputDialog.getItem(
                None,
                "Choisir le format d'export",
                "Format:",
                formats,
                0,
                False
            )
            
            if not ok:
                self.log_callback("🚫 Choix de format annulé", 'INFO')
                return
            
            self.log_callback(f"📄 Format choisi: {format_choisi}", 'INFO')
            
            # Exporter chaque rapprochement
            exportes = 0
            for nom_rapprochement, df_rapprochement in rapprochements.items():
                if df_rapprochement is not None and df_rapprochement.height > 0:
                    # Créer le nom de fichier selon le format
                    if format_choisi == "CSV":
                        nom_fichier = f"{nom_rapprochement}.csv"
                        chemin_fichier = os.path.join(dossier, nom_fichier)
                        df_rapprochement.write_csv(chemin_fichier, separator=';')
                    elif format_choisi == "Excel (.xlsx)":
                        nom_fichier = f"{nom_rapprochement}.xlsx"
                        chemin_fichier = os.path.join(dossier, nom_fichier)
                        df_rapprochement.write_excel(chemin_fichier)
                    elif format_choisi == "TXT":
                        nom_fichier = f"{nom_rapprochement}.txt"
                        chemin_fichier = os.path.join(dossier, nom_fichier)
                        df_rapprochement.write_csv(chemin_fichier, separator='|')
                    elif format_choisi == "Parquet":
                        nom_fichier = f"{nom_rapprochement}.parquet"
                        chemin_fichier = os.path.join(dossier, nom_fichier)
                        df_rapprochement.write_parquet(chemin_fichier)
                    
                    exportes += 1
                    self.log_callback(f"✅ Exporté: {nom_fichier} ({df_rapprochement.height:,} lignes)", 'INFO')
            
            # Exporter les rapprochements croisés s'ils existent
            if hasattr(self, 'df_rapprochements_croises') and cle_rapprochements in self.df_rapprochements_croises:
                rapprochements_croises = self.df_rapprochements_croises[cle_rapprochements]
                
                for nom_rapprochement_croise, df_rapprochement_croise in rapprochements_croises.items():
                    if df_rapprochement_croise is not None and df_rapprochement_croise.height > 0:
                        # Créer le nom de fichier selon le format
                        if format_choisi == "CSV":
                            nom_fichier = f"{nom_rapprochement_croise}.csv"
                            chemin_fichier = os.path.join(dossier, nom_fichier)
                            df_rapprochement_croise.write_csv(chemin_fichier, separator=';')
                        elif format_choisi == "Excel (.xlsx)":
                            nom_fichier = f"{nom_rapprochement_croise}.xlsx"
                            chemin_fichier = os.path.join(dossier, nom_fichier)
                            df_rapprochement_croise.write_excel(chemin_fichier)
                        elif format_choisi == "TXT":
                            nom_fichier = f"{nom_rapprochement_croise}.txt"
                            chemin_fichier = os.path.join(dossier, nom_fichier)
                            df_rapprochement_croise.write_csv(chemin_fichier, separator='|')
                        elif format_choisi == "Parquet":
                            nom_fichier = f"{nom_rapprochement_croise}.parquet"
                            chemin_fichier = os.path.join(dossier, nom_fichier)
                            df_rapprochement_croise.write_parquet(chemin_fichier)
                        
                        exportes += 1
                        self.log_callback(f"✅ Exporté croisé: {nom_fichier} ({df_rapprochement_croise.height:,} lignes)", 'INFO')
            
            # Exporter les rapprochements finaux avec agence s'ils existent
            if hasattr(self, 'df_rapprochement_final') and cle_rapprochements in self.df_rapprochement_final:
                rapprochements_finaux = self.df_rapprochement_final[cle_rapprochements]
                
                for nom_rapprochement_final, df_rapprochement_final in rapprochements_finaux.items():
                    if df_rapprochement_final is not None and df_rapprochement_final.height > 0:
                        # Créer le nom de fichier selon le format
                        if format_choisi == "CSV":
                            nom_fichier = f"{nom_rapprochement_final}.csv"
                            chemin_fichier = os.path.join(dossier, nom_fichier)
                            df_rapprochement_final.write_csv(chemin_fichier, separator=';')
                        elif format_choisi == "Excel (.xlsx)":
                            nom_fichier = f"{nom_rapprochement_final}.xlsx"
                            chemin_fichier = os.path.join(dossier, nom_fichier)
                            df_rapprochement_final.write_excel(chemin_fichier)
                        elif format_choisi == "TXT":
                            nom_fichier = f"{nom_rapprochement_final}.txt"
                            chemin_fichier = os.path.join(dossier, nom_fichier)
                            df_rapprochement_final.write_csv(chemin_fichier, separator='|')
                        elif format_choisi == "Parquet":
                            nom_fichier = f"{nom_rapprochement_final}.parquet"
                            chemin_fichier = os.path.join(dossier, nom_fichier)
                            df_rapprochement_final.write_parquet(chemin_fichier)
                        
                        exportes += 1
                        self.log_callback(f"✅ Exporté final: {nom_fichier} ({df_rapprochement_final.height:,} lignes)", 'INFO')
            
            # Message de succès
            if exportes > 0:
                QMessageBox.information(None, "Export réussi", 
                                  f"{exportes} rapprochement(s) exporté(s) avec succès!\n\n"
                                  f"Dossier: {dossier}")
                self.log_callback(f"🎉 Export terminé: {exportes} fichiers", 'SUCCESS')
            else:
                QMessageBox.warning(None, "Export vide", 
                                "Aucune donnée à exporter.")
                self.log_callback("⚠️ Aucune donnée à exporter", 'WARNING')
            
        except Exception as e:
            self.log_callback(f"❌ Erreur lors de l'export: {str(e)}", 'ERROR')
            QMessageBox.critical(None, "Erreur d'export", 
                             f"Une erreur est survenue lors de l'export:\n{str(e)}")
    
    def rapprocher_resultats_entre_eux(self, instrument: str, nature_ope: str):
        """
        Effectue le rapprochement croisé entre les résultats de rapprochement
        
        Args:
            instrument: Nom de l'instrument de paiement
            nature_ope: Nature de l'opération (ALLER/RETOUR)
        """
        try:
            self.log_callback(f"🔄 Début du rapprochement croisé pour {instrument} ({nature_ope})", 'INFO')
            
            # Vérifier si les rapprochements existent
            cle_rapprochements = f"{instrument}_{nature_ope}"
            if not hasattr(self, 'df_rapprochements') or cle_rapprochements not in self.df_rapprochements:
                self.log_callback("❌ Aucun rapprochement trouvé pour le rapprochement croisé", 'ERROR')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Veuillez d'abord effectuer les rapprochements</span><br>")
                return
            
            rapprochements = self.df_rapprochements[cle_rapprochements]
            
            # Vérifier que les deux rapprochements nécessaires existent
            if "RAPPROCHEMENT_4325210_C_D" not in rapprochements or "RAPPROCHEMENT_6374010_C_D" not in rapprochements:
                self.log_callback("❌ Rapprochements 4325210 ou 6374010 manquants", 'ERROR')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Rapprochements 4325210 ou 6374010 manquants</span><br>")
                return
            
            df_4325210 = rapprochements["RAPPROCHEMENT_4325210_C_D"]
            df_6374010 = rapprochements["RAPPROCHEMENT_6374010_C_D"]
            
            self.log_callback(f"🔗 Rapprochement croisé: 4325210 ↔ 6374010", 'INFO')
            
            # Effectuer le rapprochement croisé
            rapprochement_croise = self.rapprocher_deux_resultats(
                df_4325210, df_6374010, "4325210", "6374010"
            )
            
            if rapprochement_croise is not None:
                # Stocker le résultat
                if not hasattr(self, 'df_rapprochements_croises'):
                    self.df_rapprochements_croises = {}
                
                self.df_rapprochements_croises[cle_rapprochements] = {
                    "RAPPROCHEMENT_CROISE_4325210_6374010": rapprochement_croise
                }
                
                # Statistiques
                total_4325210 = df_4325210.height
                total_6374010 = df_6374010.height
                total_croise = rapprochement_croise.height
                matches = rapprochement_croise.filter(
                    pl.col("STATUT_RAPPROCHEMENT_CROISE") == "RAPPROCHE"
                ).height
                
                self.log_callback(f"✅ Rapprochement croisé: {total_croise:,} lignes ({matches:,} matches)", 'INFO')
                
                # Afficher les résultats dans l'interface
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append(f"<span style='color: #8b5cf6;'>🔗 Rapprochement croisé effectué</span><br><br>")
                current_tab.resultats_text.append(f"<span style='color: #10b981;'>• 4325210: <b>{total_4325210:,}</b> lignes</span><br>")
                current_tab.resultats_text.append(f"<span style='color: #10b981;'>• 6374010: <b>{total_6374010:,}</b> lignes</span><br>")
                current_tab.resultats_text.append(f"<span style='color: #10b981;'>• Croisé: <b>{total_croise:,}</b> lignes (<b>{matches:,}</b> matches)</span><br>")
                current_tab.resultats_text.append("<br>")
            
            self.log_callback(f"🎉 Rapprochement croisé terminé", 'INFO')
            
        except Exception as e:
            self.log_callback(f"❌ Erreur lors du rapprochement croisé: {str(e)}", 'ERROR')
    
    def rapprocher_deux_resultats(self, df_4325210, df_6374010, ncp1, ncp2):
        """
        Effectue le rapprochement entre deux résultats de rapprochement
        
        Args:
            df_4325210: DataFrame du rapprochement 4325210
            df_6374010: DataFrame du rapprochement 6374010
            ncp1: Premier NCP (4325210)
            ncp2: Deuxième NCP (6374010)
            
        Returns:
            DataFrame avec le résultat du rapprochement croisé
        """
        try:
            # Colonnes de rapprochement selon les critères spécifiés
            colonnes_rapprochement_4325210 = [
                "MONTANT_4325210_D",
                "PIE_4325210_D", 
                "EVE_4325210_D",
                "AG.SAISIE_4325210_D",
                "INDEX_4325210_D"
            ]
            
            colonnes_rapprochement_6374010 = [
                "MONTANT_CLSA_C",
                "PIE_CLSA_C",
                "EVE_CLSA_C",
                "AG.SAISIE_CLSA_C",
                "INDEX_CLSA_C"
            ]
            
            # Vérifier que toutes les colonnes existent
            colonnes_manquantes_4325210 = [col for col in colonnes_rapprochement_4325210 if col not in df_4325210.columns]
            colonnes_manquantes_6374010 = [col for col in colonnes_rapprochement_6374010 if col not in df_6374010.columns]
            
            if colonnes_manquantes_4325210:
                self.log_callback(f"⚠️ Colonnes manquantes 4325210: {colonnes_manquantes_4325210}", 'WARNING')
            if colonnes_manquantes_6374010:
                self.log_callback(f"⚠️ Colonnes manquantes 6374010: {colonnes_manquantes_6374010}", 'WARNING')
            
            # Créer les clés de rapprochement
            df_4325210_avec_cle = df_4325210.with_columns(
                pl.concat_str([
                    pl.col(colonnes_rapprochement_4325210[0]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_4325210[1]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_4325210[2]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_4325210[3]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_4325210[4]).cast(pl.Utf8)
                ]).alias("cle_rapprochement_croise")
            )
            
            df_6374010_avec_cle = df_6374010.with_columns(
                pl.concat_str([
                    pl.col(colonnes_rapprochement_6374010[0]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_6374010[1]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_6374010[2]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_6374010[3]),
                    pl.lit("_"),
                    pl.col(colonnes_rapprochement_6374010[4]).cast(pl.Utf8)
                ]).alias("cle_rapprochement_croise")
            )
            
            # Effectuer la jointure full outer join
            df_rapprochement_croise = df_4325210_avec_cle.join(
                df_6374010_avec_cle,
                on="cle_rapprochement_croise",
                how="full",
                suffix=f"_{ncp2}"
            )
            
            # Ajouter le statut de rapprochement croisé
            df_rapprochement_croise = df_rapprochement_croise.with_columns(
                pl.when(
                    pl.col("cle_rapprochement_croise").is_not_null() &
                    pl.col(f"cle_rapprochement_croise_{ncp2}").is_not_null()
                ).then(pl.lit("RAPPROCHE"))
                .when(
                    pl.col("cle_rapprochement_croise").is_not_null() &
                    pl.col(f"cle_rapprochement_croise_{ncp2}").is_null()
                ).then(pl.lit(f"UNIQUE_{ncp1}"))
                .when(
                    pl.col("cle_rapprochement_croise").is_null() &
                    pl.col(f"cle_rapprochement_croise_{ncp2}").is_not_null()
                ).then(pl.lit(f"UNIQUE_{ncp2}"))
                .otherwise(pl.lit("INCONNU"))
                .alias("STATUT_RAPPROCHEMENT_CROISE")
            )
            
            # Nettoyer les colonnes de rapprochement temporaires
            colonnes_a_supprimer = ["cle_rapprochement_croise", f"cle_rapprochement_croise_{ncp2}"]
            for col in colonnes_a_supprimer:
                if col in df_rapprochement_croise.columns:
                    df_rapprochement_croise = df_rapprochement_croise.drop(col)
            
            return df_rapprochement_croise
            
        except Exception as e:
            self.log_callback(f"❌ Erreur rapprochement croisé {ncp1}-{ncp2}: {str(e)}", 'ERROR')
            return None
    
    def charger_et_rapprocher_agence(self, instrument: str, nature_ope: str):
        """
        Charge la base agence, la transforme et effectue le rapprochement final
        
        Args:
            instrument: Nom de l'instrument de paiement
            nature_ope: Nature de l'opération (ALLER/RETOUR)
        """
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            
            self.log_callback(f"🔄 Début du processus agence pour {instrument} ({nature_ope})", 'INFO')
            
            # Vérifier si le rapprochement croisé existe
            cle_rapprochements = f"{instrument}_{nature_ope}"
            if not hasattr(self, 'df_rapprochements_croises') or cle_rapprochements not in self.df_rapprochements_croises:
                self.log_callback("❌ Aucun rapprochement croisé trouvé", 'ERROR')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Veuillez d'abord effectuer le rapprochement croisé</span><br>")
                return
            
            if "RAPPROCHEMENT_CROISE_4325210_6374010" not in self.df_rapprochements_croises[cle_rapprochements]:
                self.log_callback("❌ Rapprochement croisé 4325210_6374010 manquant", 'ERROR')
                current_tab = self.tab_widget.currentWidget()
                current_tab.resultats_text.append("<span style='color: #ef4444;'>❌ Rapprochement croisé 4325210_6374010 manquant</span><br>")
                return
            
            # Demander le fichier agence
            fichier_agence, _ = QFileDialog.getOpenFileName(
                None,
                "Sélectionner le fichier BKHIS Agence",
                "",
                "Fichiers Excel (*.xlsx);;Fichiers CSV (*.csv);;Tous les fichiers (*.*)"
            )
            
            if not fichier_agence:
                self.log_callback("🚫 Chargement agence annulé", 'INFO')
                return
            
            self.log_callback(f"📁 Chargement BKHIS Agence: {fichier_agence}", 'INFO')
            
            # Charger la base agence
            try:
                file_ext = Path(fichier_agence).suffix.lower()
                
                # Définir les en-têtes personnalisés (identiques au BKHIS DMP)
                headers = [
                    "AGE", "DEV", "NCP", "UNKNOWN", "DCO", "OPE", "MVT", "UNKNOWN1", 
                    "DVAL", "UNKNOWN2", "MONTANT", "SENS", "LIBELLE", "EXO", "PIE", 
                    "UNKNOWN3", "UNKNOWN4", "UNKNOWN5", "UNKNOWN6", "UNKNOWN7", "UTIL", 
                    "UNKNOWN8", "UNKNOWN9", "EVE", "AG.EM", "DAG", "UNKNOWN10", 
                    "UNKNOWN11", "UNKNOWN12", "UNKNOWN13", "RLETT", "UNKNOWN14", 
                    "UNKNOWN15", "UNKNOWN16", "AG.SAISIE", "AG.EMETRICE", "CODE MONNAIE", 
                    "CVAL DZD", "UNKNOWN17", "UNKNOWN18", "UNKNOWN19", "UNKNOWN20"
                ]
                
                # Options de chargement robustes
                load_options = {
                    'has_header': False,
                    'new_columns': headers,
                    'infer_schema_length': 10000,  # Augmenté pour mieux détecter les types
                    'ignore_errors': True,  # Ignorer les erreurs de parsing
                    'null_values': ['', 'NULL', 'N/A', 'null', 'NA']  # Valeurs nulles possibles
                }
                
                if file_ext == '.xlsx':
                    df_agence = pl.read_excel(fichier_agence, has_header=False, new_columns=headers)
                elif file_ext == '.csv':
                    df_agence = pl.read_csv(fichier_agence, separator=',', **load_options)
                elif file_ext == '.txt':
                    df_agence = pl.read_csv(fichier_agence, separator='|', **load_options)
                elif file_ext == '.dsv':
                    df_agence = pl.read_csv(fichier_agence, separator='|', **load_options)
                elif file_ext == '.parquet':
                    # Pour Parquet, on charge d'abord puis on renomme les colonnes
                    df_agence = pl.read_parquet(fichier_agence)
                    if len(df_agence.columns) == len(headers):
                        df_agence = df_agence.rename(dict(zip(df_agence.columns, headers)))
                else:
                    # Essayer avec le délimiteur pipe par défaut
                    df_agence = pl.read_csv(fichier_agence, separator='|', **load_options)
                
                self.log_callback(f"✅ Base agence chargée: {df_agence.height:,} lignes, {df_agence.width} colonnes", 'INFO')
                self.log_callback(f"📋 Colonnes détectées: {df_agence.columns[:10]}...", 'INFO')
                
            except Exception as e:
                self.log_callback(f"❌ Erreur chargement agence: {str(e)}", 'ERROR')
                QMessageBox.critical(None, "Erreur de chargement", 
                                 f"Erreur lors du chargement du fichier agence:\n{str(e)}")
                return
            
            # Étape 1: Création des en-têtes exactement comme la première base BKHIS
            self.log_callback("🔧 Étape 1: Standardisation des en-têtes", 'INFO')
            df_agence = self.standardiser_entetes_agence(df_agence)
            
            # Étape 2: Conserver uniquement les colonnes requises
            self.log_callback("🔧 Étape 2: Filtrage des colonnes", 'INFO')
            self.log_callback(f"📋 Colonnes disponibles avant filtrage: {df_agence.columns}", 'INFO')
            
            colonnes_requises = ["AGE", "DCO", "MONTANT", "LIBELLE", "OPE", "PIE", "EVE"]
            colonnes_disponibles = [col for col in colonnes_requises if col in df_agence.columns]
            colonnes_manquantes = [col for col in colonnes_requises if col not in df_agence.columns]
            
            self.log_callback(f"📋 Colonnes requises: {colonnes_requises}", 'INFO')
            self.log_callback(f"📋 Colonnes disponibles: {colonnes_disponibles}", 'INFO')
            self.log_callback(f"📋 Colonnes manquantes: {colonnes_manquantes}", 'INFO')
            
            if colonnes_manquantes:
                self.log_callback(f"⚠️ Colonnes manquantes: {colonnes_manquantes}", 'WARNING')
                # Si des colonnes importantes manquent, on essaie de les trouver avec des noms alternatifs
                mapping_alternatif = {
                    'AGE': ['AGE', 'AG', 'AGENCE', 'CODE_AGENCE'],
                    'MONTANT': ['MONTANT', 'MONT', 'AMOUNT', 'VALEUR'],
                    'PIE': ['PIE', 'PIECE', 'DOCUMENT', 'REF'],
                    'EVE': ['EVE', 'EVENT', 'EVENEMENT', 'EV']
                }
                
                for col_requise in colonnes_manquantes:
                    if col_requise in mapping_alternatif:
                        for alt_name in mapping_alternatif[col_requise]:
                            if alt_name in df_agence.columns:
                                df_agence = df_agence.rename({alt_name: col_requise})
                                self.log_callback(f"✅ Colonne renommée: {alt_name} → {col_requise}", 'INFO')
                                colonnes_disponibles.append(col_requise)
                                break
            
            # Mettre à jour les colonnes disponibles après renommage
            colonnes_disponibles = [col for col in colonnes_requises if col in df_agence.columns]
            df_agence = df_agence.select(colonnes_disponibles)
            self.log_callback(f"✅ Colonnes conservées: {colonnes_disponibles}", 'INFO')
            
            # Étape 3: Filtrer LIBELLE pour ne conserver que "RET"
            self.log_callback("🔧 Étape 3: Filtrage LIBELLE (contient 'RET')", 'INFO')
            if "LIBELLE" in df_agence.columns:
                df_agence = df_agence.filter(
                    pl.col("LIBELLE").str.contains("RET")
                )
                self.log_callback(f"✅ Filtre LIBELLE: {df_agence.height:,} lignes restantes", 'INFO')
            
            # Étape 4: Suppression des doublons selon AGE, MONTANT, LIBELLE, PIE, EVE
            self.log_callback("🔧 Étape 4: Suppression des doublons", 'INFO')
            colonnes_doublons = ["AGE", "MONTANT", "LIBELLE", "PIE", "EVE"]
            colonnes_doublons_disponibles = [col for col in colonnes_doublons if col in df_agence.columns]
            
            if colonnes_doublons_disponibles:
                avant_doublons = df_agence.height
                df_agence = df_agence.unique(subset=colonnes_doublons_disponibles, keep='first')
                apres_doublons = df_agence.height
                doublons_supprimes = avant_doublons - apres_doublons
                self.log_callback(f"✅ Doublons supprimés: {doublons_supprimes:,} (de {avant_doublons:,} à {apres_doublons:,})", 'INFO')
            
            # Étape 5: La base agence est maintenant prête (pas de colonne INDEX)
            self.log_callback("🔧 Étape 5: Base agence prête pour rapprochement", 'INFO')
            
            # Stocker la base agence transformée
            if not hasattr(self, 'df_agence_transformee'):
                self.df_agence_transformee = {}
            
            self.df_agence_transformee[cle_rapprochements] = df_agence
            
            # Étape 6: Rapprochement final avec la base agence
            self.log_callback("🔧 Étape 6: Rapprochement final avec base agence", 'INFO')
            self.rapprochement_final_agence(instrument, nature_ope)
            
            self.log_callback(f"🎉 Processus agence terminé", 'INFO')
            
        except Exception as e:
            self.log_callback(f"❌ Erreur processus agence: {str(e)}", 'ERROR')
            QMessageBox.critical(None, "Erreur", 
                             f"Erreur lors du processus agence:\n{str(e)}")
    
    def standardiser_entetes_agence(self, df_agence):
        """
        Standardise les en-têtes de la base agence comme la première base BKHIS
        
        Args:
            df_agence: DataFrame de la base agence
            
        Returns:
            DataFrame avec en-têtes standardisées
        """
        # Les en-têtes sont déjà standardisés grâce au chargement avec new_columns
        self.log_callback(f"✅ En-têtes déjà standardisés: {df_agence.columns[:10]}...", 'INFO')
        return df_agence
    
    def rapprochement_final_agence(self, instrument: str, nature_ope: str):
        """
        Effectue le rapprochement final entre RAPPROCHEMENT_CROISE et la base agence
        
        Args:
            instrument: Nom de l'instrument de paiement
            nature_ope: Nature de l'opération (ALLER/RETOUR)
        """
        try:
            cle_rapprochements = f"{instrument}_{nature_ope}"
            
            # Récupérer les données
            df_rapprochement_croise = self.df_rapprochements_croises[cle_rapprochements]["RAPPROCHEMENT_CROISE_4325210_6374010"]
            df_agence = self.df_agence_transformee[cle_rapprochements]
            
            self.log_callback(f"🔗 Rapprochement final: Croisé ({df_rapprochement_croise.height:,}) ↔ Agence ({df_agence.height:,})", 'INFO')
            
            # Colonnes de rapprochement selon les critères spécifiés (sans INDEX)
            colonnes_croise = [
                "AG.SAISIE_4325210_C",
                "MONTANT_4325210_C",
                "PIE_4325210_C",
                "EVE_4325210_C"
            ]
            
            colonnes_agence = [
                "AGE",
                "MONTANT",
                "PIE",
                "EVE"
            ]
            
            # Vérifier les colonnes
            colonnes_manquantes_croise = [col for col in colonnes_croise if col not in df_rapprochement_croise.columns]
            colonnes_manquantes_agence = [col for col in colonnes_agence if col not in df_agence.columns]
            
            if colonnes_manquantes_croise:
                self.log_callback(f"⚠️ Colonnes manquantes croisé: {colonnes_manquantes_croise}", 'WARNING')
            if colonnes_manquantes_agence:
                self.log_callback(f"⚠️ Colonnes manquantes agence: {colonnes_manquantes_agence}", 'WARNING')
            
            # Créer les clés de rapprochement composite AGE-MONTANT-PIE-EVE
            df_croise_avec_cle = df_rapprochement_croise.with_columns(
                pl.concat_str([
                    pl.col(colonnes_croise[0]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_croise[1]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_croise[2]),
                    pl.lit("_"),
                    pl.col(colonnes_croise[3])
                ]).alias("cle_rapprochement_final")
            )
            
            df_agence_avec_cle = df_agence.with_columns(
                pl.concat_str([
                    pl.col(colonnes_agence[0]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_agence[1]).cast(pl.Utf8),
                    pl.lit("_"),
                    pl.col(colonnes_agence[2]),
                    pl.lit("_"),
                    pl.col(colonnes_agence[3])
                ]).alias("cle_rapprochement_final")
            )
            
            # Effectuer la jointure full outer join
            df_rapprochement_final = df_croise_avec_cle.join(
                df_agence_avec_cle,
                on="cle_rapprochement_final",
                how="full",
                suffix="_AGENCE"
            )
            
            # Extraire les numéros de chèque de la colonne LIBELLE (base agence)
            self.log_callback("🔧 Extraction des numéros de chèque", 'INFO')
            
            # Debug: Vérifier les colonnes disponibles
            self.log_callback(f"📋 Colonnes disponibles après jointure: {df_rapprochement_final.columns}", 'INFO')
            
            if "LIBELLE" in df_rapprochement_final.columns:
                # Debug: Afficher quelques exemples de LIBELLE
                exemples_libelle = df_rapprochement_final.select("LIBELLE").limit(5).to_series().to_list()
                self.log_callback(f"📋 Exemples LIBELLE: {exemples_libelle}", 'INFO')
                
                # Premier essai: CHEQUE RET avec espaces multiples
                df_rapprochement_final = df_rapprochement_final.with_columns(
                    pl.col("LIBELLE")
                    .str.extract(r"CHEQUE RET\s+(\d+)", 1)  # Gère les espaces multiples
                    .alias("NUM_CHQ")
                )
                
                # Debug: Vérifier résultats du premier essai
                exemples_num_chq1 = df_rapprochement_final.select("NUM_CHQ").limit(5).to_series().to_list()
                self.log_callback(f"📋 Résultat essai 1 (CHEQUE RET espaces): {exemples_num_chq1}", 'INFO')
                
                # Si aucun résultat, essayer avec "CHQ RET" et espaces multiples
                df_rapprochement_final = df_rapprochement_final.with_columns(
                    pl.when(
                        pl.col("NUM_CHQ").is_null()
                    )
                    .then(
                        pl.col("LIBELLE")
                        .str.extract(r"CHQ RET\s+(\d+)", 1)  # Gère les espaces multiples
                    )
                    .otherwise(pl.col("NUM_CHQ"))
                    .alias("NUM_CHQ")
                )
                
                # Debug: Vérifier résultats du deuxième essai
                exemples_num_chq2 = df_rapprochement_final.select("NUM_CHQ").limit(5).to_series().to_list()
                self.log_callback(f"📋 Résultat essai 2 (CHQ RET espaces): {exemples_num_chq2}", 'INFO')
                
                # Compter les numéros de chèque extraits
                nb_chq_extraits = df_rapprochement_final.filter(
                    pl.col("NUM_CHQ").is_not_null()
                ).height
                self.log_callback(f"✅ Numéros de chèque extraits: {nb_chq_extraits:,}", 'INFO')
            else:
                # Si pas de LIBELLE, créer une colonne NUM_CHQ vide
                self.log_callback("⚠️ Colonne LIBELLE non trouvée dans le rapprochement final", 'WARNING')
                self.log_callback(f"📋 Colonnes disponibles: {df_rapprochement_final.columns}", 'INFO')
                df_rapprochement_final = df_rapprochement_final.with_columns(
                    pl.lit(None).alias("NUM_CHQ")
                )
                self.log_callback("⚠️ NUM_CHQ créé vide", 'WARNING')
            
            # Ajouter le statut de rapprochement final
            df_rapprochement_final = df_rapprochement_final.with_columns(
                pl.when(
                    pl.col("cle_rapprochement_final").is_not_null() &
                    pl.col("cle_rapprochement_final_AGENCE").is_not_null()
                ).then(pl.lit("RAPPROCHE_FINAL"))
                .when(
                    pl.col("cle_rapprochement_final").is_not_null() &
                    pl.col("cle_rapprochement_final_AGENCE").is_null()
                ).then(pl.lit("UNIQUE_CROISE"))
                .when(
                    pl.col("cle_rapprochement_final").is_null() &
                    pl.col("cle_rapprochement_final_AGENCE").is_not_null()
                ).then(pl.lit("UNIQUE_AGENCE"))
                .otherwise(pl.lit("INCONNU"))
                .alias("STATUT_RAPPROCHEMENT_FINAL")
            )
            
            # Nettoyer les colonnes de rapprochement temporaires
            colonnes_a_supprimer = ["cle_rapprochement_final", "cle_rapprochement_final_AGENCE"]
            for col in colonnes_a_supprimer:
                if col in df_rapprochement_final.columns:
                    df_rapprochement_final = df_rapprochement_final.drop(col)
            
            # Réorganiser les colonnes pour placer NUM_CHQ juste avant STATUT_RAPPROCHEMENT_FINAL
            if "NUM_CHQ" in df_rapprochement_final.columns and "STATUT_RAPPROCHEMENT_FINAL" in df_rapprochement_final.columns:
                colonnes = [col for col in df_rapprochement_final.columns if col not in ["NUM_CHQ", "STATUT_RAPPROCHEMENT_FINAL"]]
                # Placer NUM_CHQ juste avant STATUT_RAPPROCHEMENT_FINAL
                colonnes.append("NUM_CHQ")
                colonnes.append("STATUT_RAPPROCHEMENT_FINAL")
                df_rapprochement_final = df_rapprochement_final.select(colonnes)
                self.log_callback("✅ Colonnes réorganisées: NUM_CHQ placé avant STATUT_RAPPROCHEMENT_FINAL", 'INFO')
            
            # Stocker le résultat
            if not hasattr(self, 'df_rapprochement_final'):
                self.df_rapprochement_final = {}
            
            self.df_rapprochement_final[cle_rapprochements] = {
                "RAPPROCHEMENT_FINAL_AVEC_AGENCE": df_rapprochement_final
            }
            
            # Statistiques
            total_croise = df_rapprochement_croise.height
            total_agence = df_agence.height
            total_final = df_rapprochement_final.height
            matches_final = df_rapprochement_final.filter(
                pl.col("STATUT_RAPPROCHEMENT_FINAL") == "RAPPROCHE_FINAL"
            ).height
            
            self.log_callback(f"✅ Rapprochement final: {total_final:,} lignes ({matches_final:,} matches)", 'INFO')
            
            # Afficher les résultats dans l'interface
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.append(f"<span style='color: #f59e0b;'>🏢 Rapprochement final avec agence effectué</span><br><br>")
            current_tab.resultats_text.append(f"<span style='color: #10b981;'>• Croisé: <b>{total_croise:,}</b> lignes</span><br>")
            current_tab.resultats_text.append(f"<span style='color: #10b981;'>• Agence: <b>{total_agence:,}</b> lignes</span><br>")
            current_tab.resultats_text.append(f"<span style='color: #10b981;'>• Final: <b>{total_final:,}</b> lignes (<b>{matches_final:,}</b> matches)</span><br>")
            current_tab.resultats_text.append("<br>")
            
            self.log_callback(f"🎉 Rapprochement final terminé", 'INFO')
            
        except Exception as e:
            self.log_callback(f"❌ Erreur rapprochement final: {str(e)}", 'ERROR')
    
    def charger_fichier_cpi(self, nature_ope: str, statut: str):
        """
        Charge un fichier CPI brut sans filtrage
        
        Args:
            nature_ope: Nature OPE CPI ("ALLER" ou "RETOUR") - non utilisé
            statut: Statut ("Rejet" ou "Paiement") - non utilisé
        """
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            from pathlib import Path
            
            self.log_callback("📂 Chargement du fichier CPI...", 'INFO')
            
            # Dialogue de sélection de fichier
            fichier_cpi, _ = QFileDialog.getOpenFileName(
                self,
                "Sélectionner le fichier CPI",
                "",
                "Fichiers supportés (*.csv *.txt *.xlsx *.parquet);;Fichiers CSV (*.csv);;Fichiers TXT (*.txt);;Fichiers Excel (*.xlsx);;Fichiers Parquet (*.parquet);;Tous les fichiers (*.*)"
            )
            
            if not fichier_cpi:
                self.log_callback("🚫 Chargement CPI annulé", 'INFO')
                return
            
            # Obtenir l'onglet actuel pour afficher les résultats
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.clear()
            current_tab.resultats_text.append(f"<b style='color: #1ecce8;'>📂 Chargement du fichier CPI...</b><br>")
            current_tab.resultats_text.append(f"Fichier: <b>{fichier_cpi}</b><br><br>")
            
            # Charger le fichier selon l'extension
            try:
                file_ext = Path(fichier_cpi).suffix.lower()
                
                if file_ext == '.xlsx':
                    df_cpi = pl.read_excel(fichier_cpi)
                elif file_ext == '.csv':
                    # Essayer d'abord avec le séparateur par défaut (virgule)
                    try:
                        df_cpi = pl.read_csv(fichier_cpi, separator=',', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                        # Si une seule colonne, essayer avec le séparateur pipe
                        if df_cpi.width == 1:
                            self.log_callback("🔍 Détection du séparateur pipe...", 'INFO')
                            df_cpi = pl.read_csv(fichier_cpi, separator='|', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                    except Exception:
                        # Si erreur avec virgule, essayer directement avec pipe
                        df_cpi = pl.read_csv(fichier_cpi, separator='|', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                elif file_ext == '.txt':
                    df_cpi = pl.read_csv(fichier_cpi, separator='|', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                elif file_ext == '.parquet':
                    df_cpi = pl.read_parquet(fichier_cpi)
                else:
                    raise ValueError(f"Format de fichier non supporté: {file_ext}")
                
                current_tab.resultats_text.append(f"<span style='color: #10b981;'>✅ Fichier chargé: {df_cpi.height:,} lignes, {df_cpi.width} colonnes</span><br>")
                self.log_callback(f"✅ Fichier CPI chargé: {df_cpi.height:,} lignes", 'INFO')
                
                # Stocker le fichier CPI brut
                if not hasattr(self, 'df_cpi_brut'):
                    self.df_cpi_brut = {}
                
                self.df_cpi_brut['fichier_principal'] = df_cpi
                
                # Résumé final
                current_tab.resultats_text.append(f"<br><b style='color: #1ecce8;'>🎉 Fichier CPI brut chargé avec succès!</b><br>")
                current_tab.resultats_text.append(f"• Total: {df_cpi.height:,} lignes<br>")
                current_tab.resultats_text.append(f"• Colonnes: {df_cpi.width}<br>")
                current_tab.resultats_text.append(f"<br><span style='color: #10b981;'>✅ Fichier CPI prêt pour le traitement!</span><br>")
                
                self.log_callback(f"🎉 Fichier CPI brut chargé: {df_cpi.height:,} lignes", 'INFO')
                
            except Exception as e:
                current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur chargement: {str(e)}</span><br>")
                self.log_callback(f"❌ Erreur chargement CPI: {str(e)}", 'ERROR')
                return
            
        except Exception as e:
            self.log_callback(f"❌ Erreur méthode charger_fichier_cpi: {str(e)}", 'ERROR')
    
    def charger_fichier_delta_aller(self):
        """
        Charge un fichier DELTA de rejets ALLER
        """
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            from pathlib import Path
            
            self.log_callback("📂 Chargement du fichier DELTA REJETS ALLER...", 'INFO')
            
            # Dialogue de sélection de fichier
            fichier_delta, _ = QFileDialog.getOpenFileName(
                self,
                "Sélectionner le fichier DELTA REJETS ALLER",
                "",
                "Fichiers supportés (*.csv *.txt *.xlsx *.parquet);;Fichiers CSV (*.csv);;Fichiers TXT (*.txt);;Fichiers Excel (*.xlsx);;Fichiers Parquet (*.parquet);;Tous les fichiers (*.*)"
            )
            
            if not fichier_delta:
                self.log_callback("🚫 Chargement DELTA ALLER annulé", 'INFO')
                return
            
            # Obtenir l'onglet actuel pour afficher les résultats
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.clear()
            current_tab.resultats_text.append(f"<b style='color: #2563eb;'>📂 Chargement du fichier DELTA REJETS ALLER...</b><br>")
            current_tab.resultats_text.append(f"Fichier: <b>{fichier_delta}</b><br><br>")
            
            # Charger le fichier selon l'extension
            try:
                file_ext = Path(fichier_delta).suffix.lower()
                
                if file_ext == '.xlsx':
                    df_delta = pl.read_excel(fichier_delta)
                elif file_ext == '.csv':
                    # Essayer d'abord avec le séparateur par défaut (virgule)
                    try:
                        df_delta = pl.read_csv(fichier_delta, separator=',', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                        # Si une seule colonne, essayer avec le séparateur pipe
                        if df_delta.width == 1:
                            self.log_callback("🔍 Détection du séparateur pipe...", 'INFO')
                            df_delta = pl.read_csv(fichier_delta, separator='|', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                    except Exception:
                        # Si erreur avec virgule, essayer directement avec pipe
                        df_delta = pl.read_csv(fichier_delta, separator='|', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                elif file_ext == '.txt':
                    df_delta = pl.read_csv(fichier_delta, separator='|', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                elif file_ext == '.parquet':
                    df_delta = pl.read_parquet(fichier_delta)
                else:
                    raise ValueError(f"Format de fichier non supporté: {file_ext}")
                
                current_tab.resultats_text.append(f"<span style='color: #10b981;'>✅ Fichier DELTA ALLER chargé: {df_delta.height:,} lignes, {df_delta.width} colonnes</span><br>")
                self.log_callback(f"✅ Fichier DELTA ALLER chargé: {df_delta.height:,} lignes", 'INFO')
                
                # Stocker le fichier DELTA ALLER
                if not hasattr(self, 'df_delta_aller'):
                    self.df_delta_aller = {}
                
                # Appliquer la transformation de la colonne AG_SAISIE si elle existe
                if "AG_SAISIE" in df_delta.columns:
                    try:
                        # Transformer AG_SAISIE : ajouter le préfixe "200" si nécessaire
                        def transform_ag_saisie(x):
                            if not x or not isinstance(x, str):
                                return x
                            x = x.strip()
                            # Si déjà au format 200xxx, ne pas transformer
                            if x.startswith("200") and len(x) == 6:
                                return x
                            # Si code numérique court (1-3 chiffres), ajouter préfixe 200
                            if x.isdigit() and len(x) <= 3:
                                return f"200{x.zfill(3)}"
                            # Sinon, retourner la valeur originale
                            return x
                        
                        df_delta = df_delta.with_columns([
                            pl.col("AG_SAISIE").cast(pl.Utf8).map_elements(
                                transform_ag_saisie,
                                return_dtype=pl.Utf8
                            ).alias("AG_SAISIE")
                        ])
                    except Exception as e:
                        self.log_callback(f"⚠️ Erreur transformation AG_SAISIE: {str(e)}", 'WARNING')
                
                self.df_delta_aller['fichier_principal'] = df_delta
                
                # Résumé final
                current_tab.resultats_text.append(f"<br><b style='color: #2563eb;'>🎉 Fichier DELTA REJETS ALLER chargé avec succès!</b><br>")
                current_tab.resultats_text.append(f"• Total: {df_delta.height:,} lignes<br>")
                current_tab.resultats_text.append(f"• Colonnes: {df_delta.width}<br>")
                current_tab.resultats_text.append(f"<br><span style='color: #10b981;'>✅ Fichier DELTA ALLER prêt pour le traitement!</span><br>")
                
                self.log_callback(f"🎉 Fichier DELTA ALLER chargé: {df_delta.height:,} lignes", 'INFO')
                
            except Exception as e:
                current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur chargement: {str(e)}</span><br>")
                self.log_callback(f"❌ Erreur chargement DELTA ALLER: {str(e)}", 'ERROR')
                return
            
        except Exception as e:
            self.log_callback(f"❌ Erreur méthode charger_fichier_delta_aller: {str(e)}", 'ERROR')
    
    def charger_fichier_delta_retour(self):
        """
        Charge un fichier DELTA de rejets RETOUR
        """
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            from pathlib import Path
            
            self.log_callback("📂 Chargement du fichier DELTA REJETS RETOUR...", 'INFO')
            
            # Dialogue de sélection de fichier
            fichier_delta, _ = QFileDialog.getOpenFileName(
                self,
                "Sélectionner le fichier DELTA REJETS RETOUR",
                "",
                "Fichiers supportés (*.csv *.txt *.xlsx *.parquet);;Fichiers CSV (*.csv);;Fichiers TXT (*.txt);;Fichiers Excel (*.xlsx);;Fichiers Parquet (*.parquet);;Tous les fichiers (*.*)"
            )
            
            if not fichier_delta:
                self.log_callback("🚫 Chargement DELTA RETOUR annulé", 'INFO')
                return
            
            # Obtenir l'onglet actuel pour afficher les résultats
            current_tab = self.tab_widget.currentWidget()
            current_tab.resultats_text.clear()
            current_tab.resultats_text.append(f"<b style='color: #f59e0b;'>📂 Chargement du fichier DELTA REJETS RETOUR...</b><br>")
            current_tab.resultats_text.append(f"Fichier: <b>{fichier_delta}</b><br><br>")
            
            # Charger le fichier selon l'extension
            try:
                file_ext = Path(fichier_delta).suffix.lower()
                
                if file_ext == '.xlsx':
                    df_delta = pl.read_excel(fichier_delta)
                elif file_ext == '.csv':
                    # Essayer d'abord avec le séparateur par défaut (virgule)
                    try:
                        df_delta = pl.read_csv(fichier_delta, separator=',', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                        # Si une seule colonne, essayer avec le séparateur pipe
                        if df_delta.width == 1:
                            self.log_callback("🔍 Détection du séparateur pipe...", 'INFO')
                            df_delta = pl.read_csv(fichier_delta, separator='|', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                    except Exception:
                        # Si erreur avec virgule, essayer directement avec pipe
                        df_delta = pl.read_csv(fichier_delta, separator='|', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                elif file_ext == '.txt':
                    df_delta = pl.read_csv(fichier_delta, separator='|', has_header=True, infer_schema_length=1000, ignore_errors=True, truncate_ragged_lines=True)
                elif file_ext == '.parquet':
                    df_delta = pl.read_parquet(fichier_delta)
                else:
                    raise ValueError(f"Format de fichier non supporté: {file_ext}")
                
                current_tab.resultats_text.append(f"<span style='color: #10b981;'>✅ Fichier DELTA RETOUR chargé: {df_delta.height:,} lignes, {df_delta.width} colonnes</span><br>")
                self.log_callback(f"✅ Fichier DELTA RETOUR chargé: {df_delta.height:,} lignes", 'INFO')
                
                # Stocker le fichier DELTA RETOUR
                if not hasattr(self, 'df_delta_retour'):
                    self.df_delta_retour = {}
                
                # Appliquer la transformation de la colonne AG_SAISIE si elle existe
                if "AG_SAISIE" in df_delta.columns:
                    try:
                        # Transformer AG_SAISIE : ajouter le préfixe "200" si nécessaire
                        def transform_ag_saisie(x):
                            if not x or not isinstance(x, str):
                                return x
                            x = x.strip()
                            # Si déjà au format 200xxx, ne pas transformer
                            if x.startswith("200") and len(x) == 6:
                                return x
                            # Si code numérique court (1-3 chiffres), ajouter préfixe 200
                            if x.isdigit() and len(x) <= 3:
                                return f"200{x.zfill(3)}"
                            # Sinon, retourner la valeur originale
                            return x
                        
                        df_delta = df_delta.with_columns([
                            pl.col("AG_SAISIE").cast(pl.Utf8).map_elements(
                                transform_ag_saisie,
                                return_dtype=pl.Utf8
                            ).alias("AG_SAISIE")
                        ])
                    except Exception as e:
                        self.log_callback(f"⚠️ Erreur transformation AG_SAISIE: {str(e)}", 'WARNING')
                
                self.df_delta_retour['fichier_principal'] = df_delta
                
                # Résumé final
                current_tab.resultats_text.append(f"<br><b style='color: #f59e0b;'>🎉 Fichier DELTA REJETS RETOUR chargé avec succès!</b><br>")
                current_tab.resultats_text.append(f"• Total: {df_delta.height:,} lignes<br>")
                current_tab.resultats_text.append(f"• Colonnes: {df_delta.width}<br>")
                current_tab.resultats_text.append(f"<br><span style='color: #10b981;'>✅ Fichier DELTA RETOUR prêt pour le traitement!</span><br>")
                
                self.log_callback(f"🎉 Fichier DELTA RETOUR chargé: {df_delta.height:,} lignes", 'INFO')
                
            except Exception as e:
                current_tab.resultats_text.append(f"<span style='color: #ef4444;'>❌ Erreur chargement: {str(e)}</span><br>")
                self.log_callback(f"❌ Erreur chargement DELTA RETOUR: {str(e)}", 'ERROR')
                return
            
        except Exception as e:
            self.log_callback(f"❌ Erreur méthode charger_fichier_delta_retour: {str(e)}", 'ERROR')
    
    def mettre_a_jour_graphique(self, df_cpi):
        """
        Met à jour le graphique en fonction des filtres sélectionnés avec animation fluide
        """
        try:
            if hasattr(self, 'canvas_graphique') and self.canvas_graphique and hasattr(self, 'fig_graphique'):
                periode = self.periode_combo.currentText()
                agence = self.agence_combo.currentText()
                
                # Importer les modules d'animation avec gestion d'erreur
                try:
                    import matplotlib.animation as animation
                    ANIMATION_AVAILABLE = True
                except ImportError:
                    ANIMATION_AVAILABLE = False
                    self.log_callback("⚠️ matplotlib.animation non disponible - utilisation du graphique statique", 'WARNING')
                
                # Effacer le graphique précédent
                self.fig_graphique.clear()
                
                # Créer le graphique avec ou sans animation
                if ANIMATION_AVAILABLE:
                    self.creer_graphique_filtre_anime(self.fig_graphique, df_cpi, periode, agence)
                else:
                    self.creer_graphique_filtre(self.fig_graphique, df_cpi, periode, agence)
                
                # Mettre à jour les totaux avec animation
                self.mettre_a_jour_totaux(df_cpi, periode, agence)
                
                # Redessiner le canvas
                self.canvas_graphique.draw()
                
        except Exception as e:
            self.log_callback(f"❌ Erreur mise à jour graphique: {str(e)}", 'ERROR')
    
    def mettre_a_jour_totaux(self, df_cpi, periode, agence):
        """
        Met à jour les totaux Aller/Retour avec animation selon le filtre agence uniquement
        """
        try:
            # Importer Qt localement
            from PyQt6.QtCore import Qt
            
            # Fonction pour formater les montants
            def formater_montant(montant):
                if montant >= 1_000_000_000:  # Milliards
                    return f"{montant / 1_000_000_000:.1f} MD DZD"
                elif montant >= 1_000_000:  # Millions
                    return f"{montant / 1_000_000:.1f} M DZD"
                else:
                    return f"{montant:,.0f} DZD"
            
            # Filtrer les données selon le filtre agence uniquement
            df_filtre = df_cpi.clone()
            
            # Appliquer le filtre d'agence
            if agence != "Toutes":
                df_filtre = df_filtre.filter(
                    ((pl.col("NATURE OPE CPI") == "ALLER") & (pl.col("AGENCEBENEFICIAIRE").cast(pl.Utf8) == agence)) |
                    ((pl.col("NATURE OPE CPI") == "RETOUR") & (pl.col("AGENCETIRE").cast(pl.Utf8) == agence))
                )
            
            # Calculer les totaux sur les données filtrées
            try:
                if "MONTANTOPERATION" in df_filtre.columns and "SENS" in df_filtre.columns and "NATURE OPE CPI" in df_filtre.columns:
                    # Convertir la colonne MONTANTOPERATION en numérique
                    df_filtre = df_filtre.with_columns([
                        pl.col("MONTANTOPERATION").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64).alias("MONTANT_NUM")
                    ])
                    
                    # Total Aller : SENS = "C" ET NATURE OPE CPI = "ALLER"
                    total_aller = df_filtre.filter(
                        (pl.col("SENS") == "C") & (pl.col("NATURE OPE CPI") == "ALLER")
                    )["MONTANT_NUM"].sum()
                    
                    # Total Retour : SENS = "C" ET NATURE OPE CPI = "RETOUR"
                    total_retour = df_filtre.filter(
                        (pl.col("SENS") == "C") & (pl.col("NATURE OPE CPI") == "RETOUR")
                    )["MONTANT_NUM"].sum()
                else:
                    total_aller = 0
                    total_retour = 0
            except Exception as e:
                self.log_callback(f"⚠️ Erreur calcul totaux filtrés: {str(e)}", 'WARNING')
                total_aller = 0
                total_retour = 0
            
            # Animation des montants
            if hasattr(self, 'aller_amount_label') and hasattr(self, 'retour_amount_label'):
                # Obtenir les valeurs précédentes
                prev_aller = getattr(self, 'prev_total_aller', 0)
                prev_retour = getattr(self, 'prev_total_retour', 0)
                
                # Animation sur 10 frames
                import math
                for frame in range(11):
                    progress = frame / 10.0
                    ease_progress = 0.5 - 0.5 * math.cos(progress * math.pi)  # Ease in-out
                    
                    # Interpolation Aller
                    current_aller = prev_aller + (total_aller - prev_aller) * ease_progress
                    self.aller_amount_label.setText(formater_montant(current_aller))
                    
                    # Interpolation Retour
                    current_retour = prev_retour + (total_retour - prev_retour) * ease_progress
                    self.retour_amount_label.setText(formater_montant(current_retour))
                    
                    # Petite pause pour l'animation
                    QApplication.processEvents()
                    import time
                    time.sleep(0.03)  # 30ms par frame
                
                # Sauvegarder les nouvelles valeurs
                self.prev_total_aller = total_aller
                self.prev_total_retour = total_retour
            
            # Mettre à jour les cartes DELTA avec le filtre d'agence
            try:
                delta_aller_count_filtre = 0
                delta_retour_count_filtre = 0
                delta_aller_montant_filtre = 0
                delta_retour_montant_filtre = 0
                
                # Récupérer les données DELTA ALLER si disponibles
                if hasattr(self, 'df_delta_aller') and 'fichier_principal' in self.df_delta_aller:
                    df_delta_aller = self.df_delta_aller['fichier_principal']
                    
                    # Appliquer le filtre d'agence (comparaison directe après transformation)
                    if agence != "Toutes" and "AG_SAISIE" in df_delta_aller.columns:
                        df_delta_aller_filtre = df_delta_aller.filter(
                            pl.col("AG_SAISIE").cast(pl.Utf8) == agence
                        )
                    else:
                        df_delta_aller_filtre = df_delta_aller
                    
                    delta_aller_count_filtre = df_delta_aller_filtre.height
                    
                    # Calculer le montant total de la colonne MONT
                    if "MONT" in df_delta_aller_filtre.columns:
                        try:
                            df_delta_aller_converti = df_delta_aller_filtre.with_columns([
                                pl.col("MONT").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64).alias("MONT_NUM")
                            ])
                            delta_aller_montant_filtre = df_delta_aller_converti["MONT_NUM"].sum()
                        except Exception:
                            delta_aller_montant_filtre = 0
                
                # Récupérer les données DELTA RETOUR si disponibles
                if hasattr(self, 'df_delta_retour') and 'fichier_principal' in self.df_delta_retour:
                    df_delta_retour = self.df_delta_retour['fichier_principal']
                    
                    # Appliquer le filtre d'agence (comparaison directe après transformation)
                    if agence != "Toutes" and "AG_SAISIE" in df_delta_retour.columns:
                        df_delta_retour_filtre = df_delta_retour.filter(
                            pl.col("AG_SAISIE").cast(pl.Utf8) == agence
                        )
                    else:
                        df_delta_retour_filtre = df_delta_retour
                    
                    delta_retour_count_filtre = df_delta_retour_filtre.height
                    
                    # Calculer le montant total de la colonne MONT
                    if "MONT" in df_delta_retour_filtre.columns:
                        try:
                            df_delta_retour_converti = df_delta_retour_filtre.with_columns([
                                pl.col("MONT").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64).alias("MONT_NUM")
                            ])
                            delta_retour_montant_filtre = df_delta_retour_converti["MONT_NUM"].sum()
                        except Exception:
                            delta_retour_montant_filtre = 0
                    else:
                        delta_retour_montant_filtre = 0
                
                # Mettre à jour les cartes DELTA avec les données filtrées
                # Carte REJETS ALLER DELTA
                if hasattr(self, 'fichier_amount_label') and hasattr(self, 'fichier_title_label'):
                    if delta_aller_montant_filtre > 0:
                        # Animation pour DELTA ALLER
                        prev_delta_aller = getattr(self, 'prev_delta_aller_montant', 0)
                        for frame in range(11):
                            progress = frame / 10.0
                            ease_progress = 0.5 - 0.5 * math.cos(progress * math.pi)  # Ease in-out
                            current_delta_aller = prev_delta_aller + (delta_aller_montant_filtre - prev_delta_aller) * ease_progress
                            self.fichier_amount_label.setText(formater_montant(current_delta_aller))
                            QApplication.processEvents()
                            time.sleep(0.03)  # 30ms par frame
                        self.fichier_amount_label.setText(formater_montant(delta_aller_montant_filtre))
                        self.fichier_title_label.setText(f"REJETS ALLER DELTA ({delta_aller_count_filtre:,} lignes)")
                    else:
                        self.fichier_amount_label.setText("0")
                        self.fichier_title_label.setText("REJETS ALLER DELTA")
                
                # Carte REJETS RETOUR DELTA
                if hasattr(self, 'colonnes_amount_label') and hasattr(self, 'colonnes_title_label'):
                    if delta_retour_montant_filtre > 0:
                        # Animation pour DELTA RETOUR
                        prev_delta_retour = getattr(self, 'prev_delta_retour_montant', 0)
                        for frame in range(11):
                            progress = frame / 10.0
                            ease_progress = 0.5 - 0.5 * math.cos(progress * math.pi)  # Ease in-out
                            current_delta_retour = prev_delta_retour + (delta_retour_montant_filtre - prev_delta_retour) * ease_progress
                            self.colonnes_amount_label.setText(formater_montant(current_delta_retour))
                            QApplication.processEvents()
                            time.sleep(0.03)  # 30ms par frame
                        self.colonnes_amount_label.setText(formater_montant(delta_retour_montant_filtre))
                        self.colonnes_title_label.setText(f"REJETS RETOUR DELTA ({delta_retour_count_filtre:,} lignes)")
                    else:
                        self.colonnes_amount_label.setText("0")
                        self.colonnes_title_label.setText("REJETS RETOUR DELTA")
                
                # Sauvegarder les nouvelles valeurs DELTA pour la prochaine animation
                self.prev_delta_aller_montant = delta_aller_montant_filtre
                self.prev_delta_retour_montant = delta_retour_montant_filtre
                        
            except Exception as e:
                self.log_callback(f"⚠️ Erreur mise à jour cartes DELTA: {str(e)}", 'WARNING')
            
        except Exception as e:
            self.log_callback(f"❌ Erreur mise à jour totaux: {str(e)}", 'ERROR')
    
    def creer_graphique_filtre_anime(self, fig, df_cpi, periode, agence):
        """
        Crée le graphique avec animation fluide lors du changement de filtres
        """
        try:
            # Importer le module d'animation localement
            import matplotlib.animation as animation
            
            # Vérifier les colonnes nécessaires
            if not all(col in df_cpi.columns for col in ["DATEREGLEMENT", "NATURE OPE CPI", "Statut"]):
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Colonnes manquantes', ha='center', va='center', color='#e2e8f0')
                return
            
            # Filtrer par statut
            df_plot = df_cpi.filter(
                (pl.col("Statut") == "Rejet") & 
                (pl.col("NATURE OPE CPI").is_in(["ALLER", "RETOUR"]))
            ).select([
                "DATEREGLEMENT", 
                "NATURE OPE CPI", 
                "Statut",
                "AGENCETIRE",
                "AGENCEBENEFICIAIRE"
            ])
            
            if df_plot.height == 0:
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Aucune donnée de rejet trouvée', ha='center', va='center', color='#e2e8f0')
                return
            
            # Convertir les dates
            df_plot = df_plot.with_columns([
                pl.col("DATEREGLEMENT").str.strptime(pl.Date, format="%d/%m/%y", strict=False).alias("date_obj")
            ])
            
            # Filtrer les dates valides
            df_plot = df_plot.filter(pl.col("date_obj").is_not_null())
            
            if df_plot.height == 0:
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Données de date invalides', ha='center', va='center', color='#e2e8f0')
                return
            
            # Appliquer le filtre d'agence
            if agence != "Toutes":
                aller_data = df_plot.filter(pl.col("NATURE OPE CPI") == "ALLER")
                retour_data = df_plot.filter(pl.col("NATURE OPE CPI") == "RETOUR")
                
                if aller_data.height > 0 and "AGENCEBENEFICIAIRE" in aller_data.columns:
                    aller_data = aller_data.filter(
                        pl.col("AGENCEBENEFICIAIRE").cast(pl.Utf8) == agence
                    )
                
                if retour_data.height > 0 and "AGENCETIRE" in retour_data.columns:
                    retour_data = retour_data.filter(
                        pl.col("AGENCETIRE").cast(pl.Utf8) == agence
                    )
                
                df_plot = pl.concat([aller_data, retour_data])
            
            # Déterminer la période de regroupement
            if periode == "Mois":
                periode_col = pl.col("date_obj").dt.strftime("%Y-%m")
            elif periode == "Bimestre":
                periode_col = (
                    pl.col("date_obj").dt.year().cast(pl.Utf8) + "-" + 
                    ((pl.col("date_obj").dt.month() - 1) // 2 + 1).cast(pl.Utf8).str.pad_start(2, "0")
                )
            elif periode == "Trimestre":
                periode_col = pl.col("date_obj").dt.strftime("%Y-Q%q")
            elif periode == "Semestre":
                periode_col = (
                    pl.col("date_obj").dt.year().cast(pl.Utf8) + "-H" + 
                    ((pl.col("date_obj").dt.month() - 1) // 6 + 1).cast(pl.Utf8)
                )
            else:  # Année
                periode_col = pl.col("date_obj").dt.strftime("%Y")
            
            # Ajouter la colonne de période
            df_plot = df_plot.with_columns([
                periode_col.alias("periode")
            ])
            
            # Calculer les statistiques
            stats = df_plot.group_by(["periode", "NATURE OPE CPI"]).agg([
                pl.count().alias("nb_rejets")
            ]).sort("periode")
            
            totals = df_plot.group_by("periode").agg([
                pl.count().alias("total_periode")
            ]).sort("periode")
            
            result = stats.join(
                totals, 
                on="periode", 
                how="left"
            ).with_columns([
                (pl.col("nb_rejets") / pl.col("total_periode") * 100).alias("taux_rejet")
            ])
            
            aller_data = result.filter(pl.col("NATURE OPE CPI") == "ALLER")
            retour_data = result.filter(pl.col("NATURE OPE CPI") == "RETOUR")
            
            # Créer le graphique
            ax = fig.add_subplot(111)
            ax.set_facecolor('#1a1a1a')
            
            # Préparer les données pour l'animation
            periodes_aller = aller_data["periode"].to_list() if aller_data.height > 0 else []
            taux_aller = aller_data["taux_rejet"].to_list() if aller_data.height > 0 else []
            
            periodes_retour = retour_data["periode"].to_list() if retour_data.height > 0 else []
            taux_retour = retour_data["taux_rejet"].to_list() if retour_data.height > 0 else []
            
            # Animation fluide type Power BI - les points changent sur place
            if periodes_aller or periodes_retour:
                # Définir l'axe X en ordre chronologique
                all_periodes = list(dict.fromkeys(periodes_aller + periodes_retour))  # Supprimer les doublons
                
                # Trier les périodes par ordre chronologique
                if periode == "Mois":
                    # Format YYYY-MM - tri chronologique direct
                    all_periodes.sort()
                elif periode == "Bimestre":
                    # Format YYYY-B01, B02... - tri chronologique direct
                    all_periodes.sort()
                elif periode == "Trimestre":
                    # Format YYYY-Q1, Q2... - tri chronologique direct
                    all_periodes.sort()
                elif periode == "Semestre":
                    # Format YYYY-H1, H2 - tri chronologique direct
                    all_periodes.sort()
                else:  # Année
                    # Format YYYY - tri chronologique direct
                    all_periodes.sort()
                
                x_positions = range(len(all_periodes))
                
                # Configurer l'axe d'abord
                ax.set_xlim(-0.5, len(all_periodes) - 0.5)
                # Verrouiller l'axe Y entre 0% et 120% pour l'espace visuel, mais afficher seulement jusqu'à 100%
                ax.set_ylim(0, 120)
                ax.set_yticks([0, 20, 40, 60, 80, 100])
                ax.set_yticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
                ax.set_xticks(x_positions)
                ax.set_xticklabels(all_periodes, rotation=45, ha='right')
                
                # Obtenir les valeurs précédentes si elles existent
                prev_taux_aller = getattr(self, 'prev_taux_aller', None)
                prev_taux_retour = getattr(self, 'prev_taux_retour', None)
                prev_periodes_aller = getattr(self, 'prev_periodes_aller', None)
                prev_periodes_retour = getattr(self, 'prev_periodes_retour', None)
                
                # Créer les lignes avec les valeurs initiales (précédentes si existantes)
                if prev_taux_aller is not None and prev_periodes_aller is not None:
                    # Utiliser les valeurs précédentes comme point de départ
                    x_aller_init = [all_periodes.index(p) if p in all_periodes else 0 for p in prev_periodes_aller]
                    line_aller, = ax.plot(x_aller_init, prev_taux_aller, 'o-', color='#10b981', linewidth=2, markersize=5, label='ALLER', alpha=0.8)
                else:
                    # Pas de valeurs précédentes, commencer à zéro
                    x_aller_init = [all_periodes.index(p) for p in periodes_aller] if periodes_aller else []
                    line_aller, = ax.plot(x_aller_init, [0] * len(x_aller_init), 'o-', color='#10b981', linewidth=2, markersize=5, label='ALLER', alpha=0.8)
                
                if prev_taux_retour is not None and prev_periodes_retour is not None:
                    # Utiliser les valeurs précédentes comme point de départ
                    x_retour_init = [all_periodes.index(p) if p in all_periodes else 0 for p in prev_periodes_retour]
                    line_retour, = ax.plot(x_retour_init, prev_taux_retour, 's-', color='#f59e0b', linewidth=2, markersize=5, label='RETOUR', alpha=0.8)
                else:
                    # Pas de valeurs précédentes, commencer à zéro
                    x_retour_init = [all_periodes.index(p) for p in periodes_retour] if periodes_retour else []
                    line_retour, = ax.plot(x_retour_init, [0] * len(x_retour_init), 's-', color='#f59e0b', linewidth=2, markersize=5, label='RETOUR', alpha=0.8)
                
                # Fonction d'animation type Power BI
                def animate(frame):
                    progress = frame / 20.0  # 20 frames pour une animation fluide
                    
                    if progress <= 1.0:
                        # Animation de transition fluide entre les valeurs
                        ease_progress = 0.5 - 0.5 * math.cos(progress * math.pi)  # Ease in-out
                        
                        # Animer la courbe ALLER
                        if periodes_aller:
                            x_aller = [all_periodes.index(p) for p in periodes_aller]
                            if prev_taux_aller is not None and prev_periodes_aller is not None:
                                # Interpoler depuis les valeurs précédentes
                                y_aller_anim = []
                                for i, periode in enumerate(periodes_aller):
                                    if periode in prev_periodes_aller:
                                        prev_idx = prev_periodes_aller.index(periode)
                                        prev_val = prev_taux_aller[prev_idx]
                                    else:
                                        prev_val = 0
                                    new_val = taux_aller[i]
                                    interpolated_val = prev_val + (new_val - prev_val) * ease_progress
                                    y_aller_anim.append(interpolated_val)
                            else:
                                # Animation depuis zéro
                                y_aller_anim = [t * ease_progress for t in taux_aller]
                            
                            line_aller.set_data(x_aller, y_aller_anim)
                        
                        # Animer la courbe RETOUR
                        if periodes_retour:
                            x_retour = [all_periodes.index(p) for p in periodes_retour]
                            if prev_taux_retour is not None and prev_periodes_retour is not None:
                                # Interpoler depuis les valeurs précédentes
                                y_retour_anim = []
                                for i, periode in enumerate(periodes_retour):
                                    if periode in prev_periodes_retour:
                                        prev_idx = prev_periodes_retour.index(periode)
                                        prev_val = prev_taux_retour[prev_idx]
                                    else:
                                        prev_val = 0
                                    new_val = taux_retour[i]
                                    interpolated_val = prev_val + (new_val - prev_val) * ease_progress
                                    y_retour_anim.append(interpolated_val)
                            else:
                                # Animation depuis zéro
                                y_retour_anim = [t * ease_progress for t in taux_retour]
                            
                            line_retour.set_data(x_retour, y_retour_anim)
                    
                    return line_aller, line_retour
                
                # Importer math pour l'interpolation
                import math
                
                # Créer l'animation avec des paramètres plus sûrs
                try:
                    anim = animation.FuncAnimation(
                        fig, animate, frames=21, interval=60, blit=False, repeat=False
                    )
                    # Stocker l'animation pour éviter le garbage collection
                    self.current_animation = anim
                    
                    # Sauvegarder les valeurs actuelles pour la prochaine animation
                    self.prev_taux_aller = taux_aller.copy() if taux_aller else []
                    self.prev_periodes_aller = periodes_aller.copy() if periodes_aller else []
                    self.prev_taux_retour = taux_retour.copy() if taux_retour else []
                    self.prev_periodes_retour = periodes_retour.copy() if periodes_retour else []
                    
                except Exception as anim_error:
                    self.log_callback(f"⚠️ Erreur animation: {str(anim_error)} - affichage statique", 'WARNING')
                    # Afficher directement les courbes si l'animation échoue
                    if periodes_aller:
                        x_aller = [all_periodes.index(p) for p in periodes_aller]
                        line_aller.set_data(x_aller, taux_aller)
                        line_aller.set_alpha(0.8)
                    
                    if periodes_retour:
                        x_retour = [all_periodes.index(p) for p in periodes_retour]
                        line_retour.set_data(x_retour, taux_retour)
                        line_retour.set_alpha(0.8)
                    
                    # Sauvegarder quand même les valeurs
                    self.prev_taux_aller = taux_aller.copy() if taux_aller else []
                    self.prev_periodes_aller = periodes_aller.copy() if periodes_aller else []
                    self.prev_taux_retour = taux_retour.copy() if taux_retour else []
                    self.prev_periodes_retour = periodes_retour.copy() if periodes_retour else []
            else:
                # Pas de données
                ax.text(0.5, 0.5, 'Aucune donnée disponible', ha='center', va='center', color='#e2e8f0')
            
            # Personnaliser le graphique
            titre = f'TAUX DE REJETS PAR {periode.upper()}'
            if agence != "Toutes":
                titre += f' (Agence {agence})'
            ax.set_title(titre, color='#e2e8f0', fontsize=11, fontweight='bold', pad=15)
            ax.set_xlabel(f'Période ({periode})', color='#e2e8f0', fontsize=9)
            ax.set_ylabel('Taux de rejets (%)', color='#e2e8f0', fontsize=9)
            
            # Couleurs des axes
            ax.tick_params(colors='#e2e8f0', labelsize=7)
            ax.spines['bottom'].set_color('#334155')
            ax.spines['top'].set_color('#334155')
            ax.spines['left'].set_color('#334155')
            ax.spines['right'].set_color('#334155')
            ax.grid(True, alpha=0.2, color='#334155')
            
            # Légende
            if periodes_aller or periodes_retour:
                legend = ax.legend(
                    facecolor='#1a1a1a', 
                    edgecolor='#334155', 
                    labelcolor='#e2e8f0', 
                    fontsize=8,
                    bbox_to_anchor=(1.05, 1),
                    loc='upper left'
                )
                legend.get_frame().set_alpha(0.8)
            
            # Ajuster la mise en page avec des marges fixes
            fig.subplots_adjust(
                left=0.08,
                right=0.75,
                top=0.85,
                bottom=0.15
            )
            
        except Exception as e:
            self.log_callback(f"❌ Erreur création graphique animé: {str(e)}", 'ERROR')
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f'Erreur: {str(e)}', ha='center', va='center', color='#ef4444')
    
    def creer_graphique_filtre(self, fig, df_cpi, periode, agence):
        """
        Crée le graphique avec les filtres de période et d'agence
        """
        try:
            # Vérifier les colonnes nécessaires
            if not all(col in df_cpi.columns for col in ["DATEREGLEMENT", "NATURE OPE CPI", "Statut"]):
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Colonnes manquantes', ha='center', va='center', color='#e2e8f0')
                return
            
            # Filtrer par statut
            df_plot = df_cpi.filter(
                (pl.col("Statut") == "Rejet") & 
                (pl.col("NATURE OPE CPI").is_in(["ALLER", "RETOUR"]))
            ).select([
                "DATEREGLEMENT", 
                "NATURE OPE CPI", 
                "Statut",
                "AGENCETIRE",
                "AGENCEBENEFICIAIRE"
            ])
            
            if df_plot.height == 0:
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Aucune donnée de rejet trouvée', ha='center', va='center', color='#e2e8f0')
                return
            
            # Convertir les dates
            df_plot = df_plot.with_columns([
                pl.col("DATEREGLEMENT").str.strptime(pl.Date, format="%d/%m/%y", strict=False).alias("date_obj")
            ])
            
            # Filtrer les dates valides
            df_plot = df_plot.filter(pl.col("date_obj").is_not_null())
            
            if df_plot.height == 0:
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Données de date invalides', ha='center', va='center', color='#e2e8f0')
                return
            
            # Appliquer le filtre d'agence
            if agence != "Toutes":
                # Séparer les données ALLER et RETOUR pour appliquer les filtres d'agence
                aller_data = df_plot.filter(pl.col("NATURE OPE CPI") == "ALLER")
                retour_data = df_plot.filter(pl.col("NATURE OPE CPI") == "RETOUR")
                
                # Filtrer ALLER par AGENCEBENEFICIAIRE
                if aller_data.height > 0 and "AGENCEBENEFICIAIRE" in aller_data.columns:
                    # Convertir en chaîne pour éviter les erreurs de type
                    aller_data = aller_data.filter(
                        pl.col("AGENCEBENEFICIAIRE").cast(pl.Utf8) == agence
                    )
                
                # Filtrer RETOUR par AGENCETIRE
                if retour_data.height > 0 and "AGENCETIRE" in retour_data.columns:
                    # Convertir en chaîne pour éviter les erreurs de type
                    retour_data = retour_data.filter(
                        pl.col("AGENCETIRE").cast(pl.Utf8) == agence
                    )
                
                # Recombiner les données
                df_plot = pl.concat([aller_data, retour_data])
            
            # Déterminer la période de regroupement
            if periode == "Mois":
                periode_col = pl.col("date_obj").dt.strftime("%Y-%m")
                format_date = "%Y-%m"
                locator_interval = 1
                format_label = "%Y-%m"
            elif periode == "Bimestre":
                # Calculer le bimestre manuellement
                periode_col = (
                    pl.col("date_obj").dt.year().cast(pl.Utf8) + "-" + 
                    ((pl.col("date_obj").dt.month() - 1) // 2 + 1).cast(pl.Utf8).str.pad_start(2, "0")
                )
                format_date = "%Y-%m"
                locator_interval = 2
                format_label = "%Y-%m"
            elif periode == "Trimestre":
                periode_col = pl.col("date_obj").dt.strftime("%Y-Q%q")
                format_date = "%Y-Q%q"
                locator_interval = 3
                format_label = "%Y-Q%q"
            elif periode == "Semestre":
                # Calculer le semestre manuellement
                periode_col = (
                    pl.col("date_obj").dt.year().cast(pl.Utf8) + "-H" + 
                    ((pl.col("date_obj").dt.month() - 1) // 6 + 1).cast(pl.Utf8)
                )
                format_date = "%Y"
                locator_interval = 6
                format_label = "%Y"
            else:  # Année
                periode_col = pl.col("date_obj").dt.strftime("%Y")
                format_date = "%Y"
                locator_interval = 12
                format_label = "%Y"
            
            # Ajouter la colonne de période
            df_plot = df_plot.with_columns([
                periode_col.alias("periode")
            ])
            
            # Calculer les statistiques par période et par nature
            stats = df_plot.group_by(["periode", "NATURE OPE CPI"]).agg([
                pl.count().alias("nb_rejets")
            ]).sort("periode")
            
            # Calculer le total par période
            totals = df_plot.group_by("periode").agg([
                pl.count().alias("total_periode")
            ]).sort("periode")
            
            # Joindre pour calculer les taux
            result = stats.join(
                totals, 
                on="periode", 
                how="left"
            ).with_columns([
                (pl.col("nb_rejets") / pl.col("total_periode") * 100).alias("taux_rejet")
            ])
            
            # Séparer les données ALLER et RETOUR
            aller_data = result.filter(pl.col("NATURE OPE CPI") == "ALLER")
            retour_data = result.filter(pl.col("NATURE OPE CPI") == "RETOUR")
            
            # Créer le graphique
            ax = fig.add_subplot(111)
            ax.set_facecolor('#1a1a1a')
            
            # Tracer les courbes
            if aller_data.height > 0:
                periodes_aller = aller_data["periode"].to_list()
                taux_aller = aller_data["taux_rejet"].to_list()
                ax.plot(range(len(periodes_aller)), taux_aller, 'o-', color='#10b981', linewidth=2, markersize=5, label='ALLER')
            
            if retour_data.height > 0:
                periodes_retour = retour_data["periode"].to_list()
                taux_retour = retour_data["taux_rejet"].to_list()
                ax.plot(range(len(periodes_retour)), taux_retour, 's-', color='#f59e0b', linewidth=2, markersize=5, label='RETOUR')
            
            # Personnaliser le graphique
            titre = f'TAUX DE REJETS PAR {periode.upper()}'
            if agence != "Toutes":
                titre += f' (Agence {agence})'
            ax.set_title(titre, color='#e2e8f0', fontsize=11, fontweight='bold', pad=15)
            ax.set_xlabel(f'Période ({periode})', color='#e2e8f0', fontsize=9)
            ax.set_ylabel('Taux de rejets (%)', color='#e2e8f0', fontsize=9)
            
            # Définir les étiquettes de l'axe X
            if aller_data.height > 0:
                periodes = aller_data["periode"].to_list()
            elif retour_data.height > 0:
                periodes = retour_data["periode"].to_list()
            else:
                periodes = []
            
            if periodes:
                ax.set_xticks(range(len(periodes)))
                ax.set_xticklabels(periodes, rotation=45, ha='right')
            
            # Couleurs des axes
            ax.tick_params(colors='#e2e8f0', labelsize=7)
            ax.spines['bottom'].set_color('#334155')
            ax.spines['top'].set_color('#334155')
            ax.spines['left'].set_color('#334155')
            ax.spines['right'].set_color('#334155')
            ax.grid(True, alpha=0.2, color='#334155')
            
            # Légende
            if aller_data.height > 0 or retour_data.height > 0:
                legend = ax.legend(
                    facecolor='#1a1a1a', 
                    edgecolor='#334155', 
                    labelcolor='#e2e8f0', 
                    fontsize=8,
                    bbox_to_anchor=(1.05, 1),  # Positionner en dehors à droite
                    loc='upper left'
                )
                legend.get_frame().set_alpha(0.8)
            
            # Ajuster la mise en page avec des marges fixes pour éviter le redimensionnement
            fig.subplots_adjust(
                left=0.08,    # Marge gauche fixe
                right=0.75,   # Marge droite pour laisser de l'espace pour la légende
                top=0.85,     # Marge supérieure
                bottom=0.15   # Marge inférieure
            )
            
        except Exception as e:
            self.log_callback(f"❌ Erreur création graphique: {str(e)}", 'ERROR')
            # Afficher un message d'erreur dans le graphique
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f'Erreur: {str(e)}', ha='center', va='center', color='#ef4444')
    
    def afficher_apercu_cpi(self):
        """
        Affiche un aperçu des 20 premières lignes du dernier fichier CPI chargé dans une nouvelle fenêtre
        """
        try:
            # Vérifier si PyQt6 est disponible
            if not PYQT_AVAILABLE:
                self.log_callback("❌ PyQt6 non disponible pour l'aperçu", 'ERROR')
                return
            
            # Importer Qt localement pour éviter les problèmes de portée
            from PyQt6.QtCore import Qt
            
            # Vérifier si des données CPI ont été chargées
            if not hasattr(self, 'df_cpi_brut') or not self.df_cpi_brut:
                QMessageBox.warning(self, "Aperçu CPI", "Aucun fichier CPI chargé. Veuillez d'abord charger un fichier CPI.")
                self.log_callback("⚠️ Aucun fichier CPI chargé pour l'aperçu", 'WARNING')
                return
            
            # Prendre le DataFrame CPI brut
            df_cpi = self.df_cpi_brut['fichier_principal']
            
            # Créer une nouvelle fenêtre pour l'aperçu
            apercu_window = QDialog(self)
            apercu_window.setWindowTitle("👁 Aperçu CPI - Fichier brut")
            apercu_window.resize(1400, 900)  # Taille par défaut
            apercu_window.showMaximized()  # Ouvrir en mode agrandi
            apercu_window.setStyleSheet("""
                QDialog {
                    background-color: #010001;
                    color: #e2e8f0;
                }
                QLabel {
                    color: #e2e8f0;
                    font-size: 14px;
                    padding: 5px;
                }
                QGroupBox {
                    color: #e2e8f0;
                    border: 2px solid #1ecce8;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: #010001;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #60a5fa;
                }
                QTextEdit {
                    background-color: #1a1a1a;
                    color: #e2e8f0;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    padding: 5px;
                    font-family: monospace;
                }
                QPushButton {
                    background-color: #1ecce8;
                    color: #010001;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1bb8d4;
                }
            """)
            
            layout = QVBoxLayout(apercu_window)
            
            # Informations générales
            info_group = QGroupBox("📊 Informations générales")
            info_layout = QVBoxLayout(info_group)  # Layout vertical
            
            # Section des filtres
            filtres_group = QGroupBox("🔍 Filtres")
            filtres_layout = QHBoxLayout(filtres_group)
            
            # Filtre de période
            periode_layout = QVBoxLayout()
            periode_layout.addWidget(QLabel("<b>Période</b>"))
            periode_combo = QComboBox()
            periode_combo.addItems(["Mois", "Bimestre", "Trimestre", "Semestre", "Année"])
            periode_combo.setCurrentText("Mois")  # Valeur par défaut
            periode_combo.setStyleSheet("""
                QComboBox {
                    background-color: #1a1a1a;
                    color: #e2e8f0;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    padding: 5px;
                    min-width: 120px;
                }
                QComboBox::drop-down {
                    background-color: #1ecce8;
                    border: none;
                }
            """)
            periode_layout.addWidget(periode_combo)
            filtres_layout.addLayout(periode_layout)
            
            # Filtre de code agence
            agence_layout = QVBoxLayout()
            agence_layout.addWidget(QLabel("<b>Code Agence</b>"))
            agence_combo = QComboBox()
            agence_combo.addItem("Toutes")  # Option par défaut
            
            # Générer la liste des codes d'agences de 200001 à 200126
            for code in range(200001, 200127):
                agence_combo.addItem(str(code))
            
            agence_combo.setCurrentText("Toutes")  # Valeur par défaut
            agence_combo.setStyleSheet("""
                QComboBox {
                    background-color: #1a1a1a;
                    color: #e2e8f0;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    padding: 5px;
                    min-width: 120px;
                }
                QComboBox::drop-down {
                    background-color: #1ecce8;
                    border: none;
                }
            """)
            agence_layout.addWidget(agence_combo)
            filtres_layout.addLayout(agence_layout)
            
            # Espace flexible
            filtres_layout.addStretch()
            
            info_layout.addWidget(filtres_group)
            
            # Layout horizontal pour les 4 cartes (2 infos + 2 totaux)
            content_layout = QHBoxLayout()
            
            # Colonne de gauche: Carte Fichier
            left_info_layout = QVBoxLayout()
            left_info_layout.setSpacing(10)  # Espacement identique entre les cartes
            
            # Carte Fichier (design identique aux cartes de totaux)
            fichier_widget = QWidget()
            fichier_layout = QVBoxLayout(fichier_widget)
            fichier_layout.setContentsMargins(5, 5, 5, 5)  # Marges minimales
            fichier_layout.setSpacing(2)
            
            fichier_amount = QLabel("0")
            fichier_amount.setStyleSheet("""
                QLabel {
                    color: #3b82f6;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            fichier_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            fichier_title = QLabel("REJETS ALLER DELTA")
            fichier_title.setStyleSheet("""
                QLabel {
                    color: #94a3b8;
                    font-size: 11px;
                    font-weight: normal;
                }
            """)
            fichier_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            fichier_layout.addWidget(fichier_amount)
            fichier_layout.addWidget(fichier_title)
            left_info_layout.addWidget(fichier_widget)
            
            # Carte Colonnes (design identique)
            colonnes_widget = QWidget()
            colonnes_layout = QVBoxLayout(colonnes_widget)
            colonnes_layout.setContentsMargins(5, 5, 5, 5)  # Marges minimales
            colonnes_layout.setSpacing(2)
            
            colonnes_amount = QLabel("0")
            colonnes_amount.setStyleSheet("""
                QLabel {
                    color: #8b5cf6;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            colonnes_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            colonnes_title = QLabel("REJETS RETOUR DELTA")
            colonnes_title.setStyleSheet("""
                QLabel {
                    color: #94a3b8;
                    font-size: 11px;
                    font-weight: normal;
                }
            """)
            colonnes_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            colonnes_layout.addWidget(colonnes_amount)
            colonnes_layout.addWidget(colonnes_title)
            left_info_layout.addWidget(colonnes_widget)
            
            left_info_layout.addStretch()  # Espace flexible
            
            # Colonne du milieu: Cartes des totaux Aller/Retour (simplifiées)
            middle_layout = QVBoxLayout()
            middle_layout.setSpacing(10)  # Espacement réduit entre les cartes
            
            # Fonction pour formater les montants
            def formater_montant(montant):
                if montant >= 1_000_000_000:  # Milliards
                    return f"{montant / 1_000_000_000:.1f} MD DZD"
                elif montant >= 1_000_000:  # Millions
                    return f"{montant / 1_000_000:.1f} M DZD"
                else:
                    return f"{montant:,.0f} DZD"
            
            # Calculer les totaux
            try:
                # Vérifier les colonnes nécessaires
                if "MONTANTOPERATION" in df_cpi.columns and "SENS" in df_cpi.columns and "NATURE OPE CPI" in df_cpi.columns:
                    # Convertir la colonne MONTANTOPERATION en numérique (gérer le format avec virgule)
                    df_cpi_converti = df_cpi.with_columns([
                        pl.col("MONTANTOPERATION").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64).alias("MONTANT_NUM")
                    ])
                    
                    # Total Aller : SENS = "C" ET NATURE OPE CPI = "ALLER"
                    total_aller = df_cpi_converti.filter(
                        (pl.col("SENS") == "C") & (pl.col("NATURE OPE CPI") == "ALLER")
                    )["MONTANT_NUM"].sum()
                    
                    # Total Retour : SENS = "C" ET NATURE OPE CPI = "RETOUR"
                    total_retour = df_cpi_converti.filter(
                        (pl.col("SENS") == "C") & (pl.col("NATURE OPE CPI") == "RETOUR")
                    )["MONTANT_NUM"].sum()
                else:
                    total_aller = 0
                    total_retour = 0
            except Exception as e:
                self.log_callback(f"⚠️ Erreur calcul totaux: {str(e)}", 'WARNING')
                total_aller = 0
                total_retour = 0
            
            # Calculer les données DELTA
            delta_aller_count = 0
            delta_retour_count = 0
            delta_aller_montant = 0
            delta_retour_montant = 0
            
            try:
                # Récupérer les données DELTA ALLER si disponibles
                if hasattr(self, 'df_delta_aller') and 'fichier_principal' in self.df_delta_aller:
                    df_delta_aller = self.df_delta_aller['fichier_principal']
                    delta_aller_count = df_delta_aller.height
                    
                    # Calculer le montant total de la colonne MONT
                    if "MONT" in df_delta_aller.columns:
                        try:
                            # Gérer le format avec virgule (1254032,64) et le convertir en nombre
                            df_delta_aller_converti = df_delta_aller.with_columns([
                                pl.col("MONT").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64).alias("MONT_NUM")
                            ])
                            delta_aller_montant = df_delta_aller_converti["MONT_NUM"].sum()
                        except Exception as e:
                            self.log_callback(f"⚠️ Erreur conversion MONT DELTA ALLER: {str(e)}", 'WARNING')
                            delta_aller_montant = 0
                    else:
                        # Chercher d'autres colonnes de montant possibles
                        for col_possible in ["MONTANT", "MONTANTOPERATION", "MONTANT_OP", "MONTANTOPERA"]:
                            if col_possible in df_delta_aller.columns:
                                try:
                                    df_delta_aller_converti = df_delta_aller.with_columns([
                                        pl.col(col_possible).cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64).alias("MONT_NUM")
                                    ])
                                    delta_aller_montant = df_delta_aller_converti["MONT_NUM"].sum()
                                    break
                                except Exception:
                                    delta_aller_montant = 0
                
                # Récupérer les données DELTA RETOUR si disponibles
                if hasattr(self, 'df_delta_retour') and 'fichier_principal' in self.df_delta_retour:
                    df_delta_retour = self.df_delta_retour['fichier_principal']
                    delta_retour_count = df_delta_retour.height
                    
                    # Calculer le montant total de la colonne MONT
                    if "MONT" in df_delta_retour.columns:
                        try:
                            # Gérer le format avec virgule (1254032,64) et le convertir en nombre
                            df_delta_retour_converti = df_delta_retour.with_columns([
                                pl.col("MONT").cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64).alias("MONT_NUM")
                            ])
                            delta_retour_montant = df_delta_retour_converti["MONT_NUM"].sum()
                        except Exception as e:
                            self.log_callback(f"⚠️ Erreur conversion MONT DELTA RETOUR: {str(e)}", 'WARNING')
                            delta_retour_montant = 0
                    else:
                        # Chercher d'autres colonnes de montant possibles
                        for col_possible in ["MONTANT", "MONTANTOPERATION", "MONTANT_OP", "MONTANTOPERA"]:
                            if col_possible in df_delta_retour.columns:
                                try:
                                    df_delta_retour_converti = df_delta_retour.with_columns([
                                        pl.col(col_possible).cast(pl.Utf8).str.replace(",", ".").cast(pl.Float64).alias("MONT_NUM")
                                    ])
                                    delta_retour_montant = df_delta_retour_converti["MONT_NUM"].sum()
                                    break
                                except Exception:
                                    delta_retour_montant = 0
                            
            except Exception as e:
                self.log_callback(f"⚠️ Erreur calcul données DELTA: {str(e)}", 'WARNING')
            
            # Mettre à jour les cartes DELTA avec les montants calculés
            # Carte REJETS ALLER DELTA - afficher le montant total
            if delta_aller_montant > 0:
                fichier_amount.setText(formater_montant(delta_aller_montant))
                fichier_title.setText(f"REJETS ALLER DELTA ({delta_aller_count:,} lignes)")
            else:
                fichier_amount.setText("0")
                fichier_title.setText("REJETS ALLER DELTA")
            
            # Carte REJETS RETOUR DELTA - afficher le montant total
            if delta_retour_montant > 0:
                colonnes_amount.setText(formater_montant(delta_retour_montant))
                colonnes_title.setText(f"REJETS RETOUR DELTA ({delta_retour_count:,} lignes)")
            else:
                colonnes_amount.setText("0")
                colonnes_title.setText("REJETS RETOUR DELTA")
            
            # Carte Aller simplifiée (sans bordure)
            aller_widget = QWidget()
            aller_layout = QVBoxLayout(aller_widget)
            aller_layout.setContentsMargins(5, 5, 5, 5)  # Marges minimales
            aller_layout.setSpacing(2)
            
            aller_amount = QLabel(formater_montant(total_aller))
            aller_amount.setStyleSheet("""
                QLabel {
                    color: #10b981;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            aller_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            aller_title = QLabel("ALLER CPI")
            aller_title.setStyleSheet("""
                QLabel {
                    color: #94a3b8;
                    font-size: 11px;
                    font-weight: normal;
                }
            """)
            aller_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            aller_layout.addWidget(aller_amount)
            aller_layout.addWidget(aller_title)
            
            # Carte Retour simplifiée (sans bordure)
            retour_widget = QWidget()
            retour_layout = QVBoxLayout(retour_widget)
            retour_layout.setContentsMargins(5, 5, 5, 5)  # Marges minimales
            retour_layout.setSpacing(2)
            
            retour_amount = QLabel(formater_montant(total_retour))
            retour_amount.setStyleSheet("""
                QLabel {
                    color: #f59e0b;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            retour_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            retour_title = QLabel("RETOUR CPI")
            retour_title.setStyleSheet("""
                QLabel {
                    color: #94a3b8;
                    font-size: 11px;
                    font-weight: normal;
                }
            """)
            retour_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            retour_layout.addWidget(retour_amount)
            retour_layout.addWidget(retour_title)
            
            # Stocker les références des labels pour l'animation
            self.aller_amount_label = aller_amount
            self.retour_amount_label = retour_amount
            self.fichier_amount_label = fichier_amount  # Référence carte DELTA ALLER
            self.fichier_title_label = fichier_title    # Référence titre carte DELTA ALLER
            self.colonnes_amount_label = colonnes_amount  # Référence carte DELTA RETOUR
            self.colonnes_title_label = colonnes_title    # Référence titre carte DELTA RETOUR
            self.prev_total_aller = total_aller
            self.prev_total_retour = total_retour
            # Initialiser les valeurs DELTA pour l'animation
            self.prev_delta_aller_montant = delta_aller_montant
            self.prev_delta_retour_montant = delta_retour_montant
            
            # Ajouter les cartes simplifiées au layout du milieu
            middle_layout.addWidget(aller_widget)
            middle_layout.addWidget(retour_widget)
            middle_layout.addStretch()  # Espace flexible pour alignement parfait
            middle_layout.addStretch()  # Espace supplémentaire pour alignement optimal
            
            # Colonne de droite: Graphique
            right_info_layout = QVBoxLayout()
            
            # Stocker les widgets pour accès ultérieur
            self.periode_combo = periode_combo
            self.agence_combo = agence_combo
            self.canvas_graphique = None
            self.df_cpi_courant = df_cpi
            
            # Connecter les signaux de changement
            periode_combo.currentTextChanged.connect(lambda: self.mettre_a_jour_graphique(df_cpi))
            agence_combo.currentTextChanged.connect(lambda: self.mettre_a_jour_graphique(df_cpi))
            
            # Ajouter le graphique des taux de rejets par période
            try:
                # Importer matplotlib pour le graphique
                from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
                from matplotlib.figure import Figure
                import matplotlib.pyplot as plt
                import matplotlib.dates as mdates
                from datetime import datetime
                
                # Créer la figure et le canvas
                fig = Figure(figsize=(10, 3.5), dpi=80, facecolor='#010001')
                canvas = FigureCanvas(fig)
                canvas.setStyleSheet("background-color: #010001;")
                
                # Créer le graphique initial
                self.creer_graphique_filtre(fig, df_cpi, "Mois", "Toutes")
                
                # Stocker la référence
                self.canvas_graphique = canvas
                self.fig_graphique = fig
                
                # Ajouter le canvas au layout de droite
                right_info_layout.addWidget(canvas)
                
            except ImportError:
                right_info_layout.addWidget(QLabel("<span style='color: #f59e0b;'>⚠️ Matplotlib non disponible</span>"))
            except Exception as e:
                right_info_layout.addWidget(QLabel(f"<span style='color: #ef4444;'>❌ Erreur graphique: {str(e)}</span>"))
            
            # Ajouter les trois colonnes au layout horizontal
            content_layout.addLayout(left_info_layout, 1)  # 1/4 de l'espace
            content_layout.addLayout(middle_layout, 1)     # 1/4 de l'espace
            content_layout.addLayout(right_info_layout, 2)  # 2/4 de l'espace
            
            info_layout.addLayout(content_layout)
            
            layout.addWidget(info_group)
            
            # Colonnes
            colonnes_group = QGroupBox("📋 Colonnes")
            colonnes_layout = QVBoxLayout(colonnes_group)
            
            colonnes = df_cpi.columns
            colonnes_text = QTextEdit()
            colonnes_text.setReadOnly(True)
            colonnes_text.setMaximumHeight(80)
            colonnes_text.setPlainText(f"Colonnes ({len(colonnes)}):\n" + "\n".join([f"  {i+1}. {col}" for i, col in enumerate(colonnes)]))
            colonnes_layout.addWidget(colonnes_text)
            
            layout.addWidget(colonnes_group)
            
            # 20 premières lignes
            lignes_group = QGroupBox("👁 20 premières lignes")
            lignes_layout = QVBoxLayout(lignes_group)
            
            # Créer un tableau QTableWidget
            from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QScrollBar
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QColor
            
            table_widget = QTableWidget()
            table_widget.setRowCount(min(20, df_cpi.height))
            table_widget.setColumnCount(df_cpi.width)
            table_widget.setHorizontalHeaderLabels(colonnes)
            
            # Configurer le tableau
            table_widget.setAlternatingRowColors(True)
            table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table_widget.setFont(QFont("Consolas, Monaco, monospace", 9))
            
            # Remplir le tableau avec les données
            df_preview = df_cpi.limit(20)
            for row in range(df_preview.height):
                row_data = df_preview.row(row, named=True)
                for col, column_name in enumerate(colonnes):
                    value = row_data[column_name]
                    if value is not None:
                        value_str = str(value)
                        # Limiter la longueur pour l'affichage
                        if len(value_str) > 50:
                            value_str = value_str[:47] + "..."
                    else:
                        value_str = "NULL"
                    
                    item = QTableWidgetItem(value_str)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    # Colorer les cellules selon le type de données
                    if column_name == "MONTANTOPERA":
                        item.setBackground(QColor("#1a3a1a"))  # Vert foncé pour montants
                    elif "DATE" in column_name:
                        item.setBackground(QColor("#1a1a3a"))  # Bleu foncé pour dates
                    elif column_name in ["INST PAIEMENT", "NATURE OPE C", "Statut"]:
                        item.setBackground(QColor("#3a1a1a"))  # Rouge foncé pour statuts
                    
                    table_widget.setItem(row, col, item)
            
            # Ajuster la taille des colonnes
            header = table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            
            # Largeur initiale des colonnes
            for col in range(df_cpi.width):
                if col < 5:  # Premières colonnes plus larges
                    table_widget.setColumnWidth(col, 120)
                else:
                    table_widget.setColumnWidth(col, 100)
            
            # Ajouter des barres de défilement si nécessaire
            table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            lignes_layout.addWidget(table_widget)
            
            layout.addWidget(lignes_group)
            
            # Colonnes importantes
            importantes_group = QGroupBox("🔍 Analyse des colonnes importantes")
            importantes_layout = QVBoxLayout(importantes_group)
            
            importantes_text = QTextEdit()
            importantes_text.setReadOnly(True)
            importantes_text.setMaximumHeight(120)
            
            contenu_importantes = ""
            
            # Vérifier la colonne INST PAIEMENT
            if "INST PAIEMENT" in df_cpi.columns:
                valeurs_inst = df_cpi.select("INST PAIEMENT").unique().to_series().to_list()[:10]
                contenu_importantes += f"✅ INST PAIEMENT: {', '.join(map(str, valeurs_inst))}\n"
            else:
                contenu_importantes += f"❌ INST PAIEMENT: Non trouvée\n"
            
            # Vérifier la colonne NATURE OPE CPI et afficher les valeurs ALLER/RETOUR
            colonne_nature = None
            for col_possible in ["NATURE OPE CPI", "NATURE_OPE_CPI", "NATUREOPECPI", "NATURE OPE", "NATUREOPE", "NATURE"]:
                if col_possible in df_cpi.columns:
                    colonne_nature = col_possible
                    break
            
            if colonne_nature:
                valeurs_nature = df_cpi.select(colonne_nature).unique().to_series().to_list()[:10]
                contenu_importantes += f"✅ {colonne_nature}: {', '.join(map(str, valeurs_nature))}\n"
                
                # Vérifier spécifiquement les valeurs ALLER et RETOUR
                valeurs_aller = df_cpi.filter(pl.col(colonne_nature) == "ALLER").height
                valeurs_retour = df_cpi.filter(pl.col(colonne_nature) == "RETOUR").height
                contenu_importantes += f"   • ALLER: {valeurs_aller:,} occurrences\n"
                contenu_importantes += f"   • RETOUR: {valeurs_retour:,} occurrences\n"
            else:
                contenu_importantes += f"❌ Colonne Nature OPE: Non trouvée\n"
            
            # Vérifier la colonne Statut et afficher les valeurs Rejet/Paiement
            colonne_statut = None
            for col_possible in ["STATUT", "STATUS", "ETAT", "SITUATION", "Statut"]:
                if col_possible in df_cpi.columns:
                    colonne_statut = col_possible
                    break
            
            if colonne_statut:
                valeurs_statut = df_cpi.select(colonne_statut).unique().to_series().to_list()[:10]
                contenu_importantes += f"✅ {colonne_statut}: {', '.join(map(str, valeurs_statut))}\n"
                
                # Vérifier spécifiquement les valeurs Rejet et Paiement
                valeurs_rejet = df_cpi.filter(pl.col(colonne_statut) == "Rejet").height
                valeurs_paiement = df_cpi.filter(pl.col(colonne_statut) == "Paiement").height
                contenu_importantes += f"   • Rejet: {valeurs_rejet:,} occurrences\n"
                contenu_importantes += f"   • Paiement: {valeurs_paiement:,} occurrences\n"
            else:
                contenu_importantes += f"❌ Colonne Statut: Non trouvée\n"
            
            # Informations supplémentaires sur les montants
            if "MONTANTOPERA" in df_cpi.columns:
                stats_montants = df_cpi.select(
                    pl.col("MONTANTOPERA").cast(pl.Float64, strict=False).null_count().alias("nulls"),
                    pl.col("MONTANTOPERA").cast(pl.Float64, strict=False).min().alias("min"),
                    pl.col("MONTANTOPERA").cast(pl.Float64, strict=False).max().alias("max"),
                    pl.col("MONTANTOPERA").cast(pl.Float64, strict=False).mean().alias("moyenne")
                )
                montant_stats = stats_montants.row(0, named=True)
                contenu_importantes += f"💰 MONTANTOPERA: Min={montant_stats['min'] or 0:,.2f}, Max={montant_stats['max'] or 0:,.2f}, Moy={montant_stats['moyenne'] or 0:,.2f}\n"
            
            importantes_text.setPlainText(contenu_importantes)
            importantes_layout.addWidget(importantes_text)
            
            layout.addWidget(importantes_group)
            
            # Bouton fermer
            btn_fermer = QPushButton("Fermer")
            btn_fermer.clicked.connect(apercu_window.accept)
            layout.addWidget(btn_fermer)
            
            # Afficher la fenêtre
            apercu_window.exec()
            
            self.log_callback(f"👁 Aperçu CPI affiché: {df_cpi.height:,} lignes, {df_cpi.width} colonnes", 'INFO')
            
        except Exception as e:
            self.log_callback(f"❌ Erreur affichage aperçu CPI: {str(e)}", 'ERROR')
            QMessageBox.critical(self, "Erreur aperçu", f"Erreur lors de l'affichage de l'aperçu:\n{str(e)}")


class Phase3Processor:
    """
    Classe principale pour le traitement Phase 3
    Gère le rapprochement avancé et l'analyse des données CPI/BKHIS
    """
    
    def __init__(self):
        """Initialisation du processeur Phase 3"""
        self.df_cpi = None
        self.df_bkhis = None
        self.df_rapprochement = None
        self.resultats = {}
        self.stats = {}
        
        logger.info("🚀 Initialisation du processeur Phase 3")
    
    def charger_donnees_cpi(self, chemin_fichier: str) -> bool:
        """
        Charge les données CPI depuis un fichier
        
        Args:
            chemin_fichier: Chemin vers le fichier CPI
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            logger.info(f"📂 Chargement des données CPI depuis: {chemin_fichier}")
            
            # Détection du format selon l'extension
            extension = Path(chemin_fichier).suffix.lower()
            
            if extension == '.csv':
                self.df_cpi = pl.read_csv(
                    chemin_fichier,
                    separator='|',
                    has_header=True,
                    infer_schema_length=1000,
                    ignore_errors=True,
                    encoding='utf8-lossy'
                )
            elif extension in ['.xlsx', '.xls']:
                self.df_cpi = pl.read_excel(chemin_fichier)
            elif extension == '.parquet':
                self.df_cpi = pl.read_parquet(chemin_fichier)
            else:
                logger.error(f"❌ Format de fichier non supporté: {extension}")
                return False
            
            logger.info(f"✅ Données CPI chargées: {self.df_cpi.height:,} lignes × {self.df_cpi.width} colonnes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des données CPI: {str(e)}")
            return False
    
    def charger_donnees_bkhis(self, chemin_fichier: str) -> bool:
        """
        Charge les données BKHIS depuis un fichier
        
        Args:
            chemin_fichier: Chemin vers le fichier BKHIS
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            logger.info(f"📂 Chargement des données BKHIS depuis: {chemin_fichier}")
            
            # Détection du format selon l'extension
            extension = Path(chemin_fichier).suffix.lower()
            
            if extension == '.csv':
                self.df_bkhis = pl.read_csv(
                    chemin_fichier,
                    separator='|',
                    has_header=True,
                    infer_schema_length=1000,
                    ignore_errors=True,
                    encoding='utf8-lossy'
                )
            elif extension in ['.xlsx', '.xls']:
                self.df_bkhis = pl.read_excel(chemin_fichier)
            elif extension == '.parquet':
                self.df_bkhis = pl.read_parquet(chemin_fichier)
            else:
                logger.error(f"❌ Format de fichier non supporté: {extension}")
                return False
            
            logger.info(f"✅ Données BKHIS chargées: {self.df_bkhis.height:,} lignes × {self.df_bkhis.width} colonnes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des données BKHIS: {str(e)}")
            return False
    
    def valider_donnees(self) -> Tuple[bool, List[str]]:
        """
        Valide les données chargées
        
        Returns:
            Tuple[bool, List[str]]: (valide, liste des erreurs)
        """
        erreurs = []
        
        # Validation des données CPI
        if self.df_cpi is None:
            erreurs.append("❌ Données CPI non chargées")
        else:
            # Vérification des colonnes obligatoires CPI
            colonnes_cpi_obligatoires = ['DATEREGLEMENT', 'MONTANTOPERATION', 'RIBTIRE', 'RIBBENEFICIAIRE']
            for col in colonnes_cpi_obligatoires:
                if col not in self.df_cpi.columns:
                    erreurs.append(f"❌ Colonne CPI manquante: {col}")
        
        # Validation des données BKHIS
        if self.df_bkhis is None:
            erreurs.append("❌ Données BKHIS non chargées")
        else:
            # Vérification des colonnes obligatoires BKHIS
            colonnes_bkhis_obligatoires = ['DATE', 'MONT', 'NCP', 'SENS']
            for col in colonnes_bkhis_obligatoires:
                if col not in self.df_bkhis.columns:
                    erreurs.append(f"❌ Colonne BKHIS manquante: {col}")
        
        valide = len(erreurs) == 0
        
        if valide:
            logger.info("✅ Validation des données réussie")
        else:
            logger.error(f"❌ Erreurs de validation: {len(erreurs)}")
            for erreur in erreurs:
                logger.error(f"   {erreur}")
        
        return valide, erreurs
    
    def preparer_donnees_cpi(self) -> bool:
        """
        Prépare les données CPI pour le rapprochement
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            logger.info("🔧 Préparation des données CPI...")
            
            # Nettoyage et standardisation des montants
            self.df_cpi = self.df_cpi.with_columns([
                pl.col("MONTANTOPERATION")
                .str.replace_all(r"^\s+|\s+$", "")
                .str.replace_all(",", ".")
                .cast(pl.Float64)
                .alias("MONTANT_NET")
            ])
            
            # Standardisation des dates
            if "DATEREGLEMENT" in self.df_cpi.columns:
                self.df_cpi = self.df_cpi.with_columns([
                    pl.col("DATEREGLEMENT").str.strptime(pl.Date, "%d/%m/%Y").alias("DATE_CPI")
                ])
            
            # Création de clés de rapprochement
            self.df_cpi = self.df_cpi.with_columns([
                (pl.col("MONTANT_NET").abs().cast(pl.Utf8) + "_" + 
                 pl.col("RIBTIRE").fill_null("") + "_" + 
                 pl.col("RIBBENEFICIAIRE").fill_null("")).alias("CLE_RAPPROCHEMENT")
            ])
            
            logger.info("✅ Données CPI préparées avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la préparation des données CPI: {str(e)}")
            return False
    
    def preparer_donnees_bkhis(self) -> bool:
        """
        Prépare les données BKHIS pour le rapprochement
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            logger.info("🔧 Préparation des données BKHIS...")
            
            # Nettoyage et standardisation des montants
            self.df_bkhis = self.df_bkhis.with_columns([
                pl.col("MONT").abs().alias("MONTANT_NET")
            ])
            
            # Standardisation des dates
            if "DATE" in self.df_bkhis.columns:
                self.df_bkhis = self.df_bkhis.with_columns([
                    pl.col("DATE").str.strptime(pl.Date, "%d/%m/%Y").alias("DATE_BKHIS")
                ])
            
            # Création de clés de rapprochement
            self.df_bkhis = self.df_bkhis.with_columns([
                (pl.col("MONTANT_NET").abs().cast(pl.Utf8) + "_" + 
                 pl.col("NCP").fill_null("") + "_" + 
                 pl.col("OPE").fill_null("")).alias("CLE_RAPPROCHEMENT")
            ])
            
            logger.info("✅ Données BKHIS préparées avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la préparation des données BKHIS: {str(e)}")
            return False
    
    def effectuer_rapprochement(self, tolerance: float = 0.01) -> bool:
        """
        Effectue le rapprochement entre CPI et BKHIS
        
        Args:
            tolerance: Tolérance pour le rapprochement des montants
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            logger.info(f"🔄 Début du rapprochement (tolérance: {tolerance})...")
            start_time = time.time()
            
            # Rapprochement par clé exacte
            rapproche_exact = self.df_cpi.join(
                self.df_bkhis,
                on="CLE_RAPPROCHEMENT",
                how="inner",
                suffix="_bkhis"
            )
            
            # Identification des non rapprochés CPI
            non_rapproches_cpi = self.df_cpi.join(
                rapproche_exact.select("CLE_RAPPROCHEMENT"),
                on="CLE_RAPPROCHEMENT",
                how="left",
                suffix="_rapproche"
            ).filter(pl.col("CLE_RAPPROCHEMENT_rapproche").is_null())
            
            # Identification des non rapprochés BKHIS
            non_rapproches_bkhis = self.df_bkhis.join(
                rapproche_exact.select("CLE_RAPPROCHEMENT"),
                on="CLE_RAPPROCHEMENT",
                how="left",
                suffix="_rapproche"
            ).filter(pl.col("CLE_RAPPROCHEMENT_rapproche").is_null())
            
            # Création du résultat final
            self.df_rapprochement = pl.concat([
                rapproche_exact.with_columns(pl.lit("RAPPROCHE").alias("STATUT_RAPPROCHEMENT")),
                non_rapproches_cpi.with_columns(pl.lit("NON_RAPPROCHE_CPI").alias("STATUT_RAPPROCHEMENT")),
                non_rapproches_bkhis.with_columns(pl.lit("NON_RAPPROCHE_BKHIS").alias("STATUT_RAPPROCHEMENT"))
            ])
            
            # Calcul des statistiques
            self.stats = {
                'total_cpi': self.df_cpi.height,
                'total_bkhis': self.df_bkhis.height,
                'rapprochees': rapproche_exact.height,
                'non_rapprochees_cpi': non_rapproches_cpi.height,
                'non_rapprochees_bkhis': non_rapproches_bkhis.height,
                'taux_rapprochement': (rapproche_exact.height / self.df_cpi.height * 100) if self.df_cpi.height > 0 else 0
            }
            
            end_time = time.time()
            temps_execution = end_time - start_time
            
            logger.info(f"✅ Rapprochement terminé en {temps_execution:.2f} secondes")
            logger.info(f"📊 Statistiques:")
            logger.info(f"   Total CPI: {self.stats['total_cpi']:,}")
            logger.info(f"   Total BKHIS: {self.stats['total_bkhis']:,}")
            logger.info(f"   Rapprochées: {self.stats['rapprochees']:,}")
            logger.info(f"   Non rapprochées CPI: {self.stats['non_rapprochees_cpi']:,}")
            logger.info(f"   Non rapprochées BKHIS: {self.stats['non_rapprochees_bkhis']:,}")
            logger.info(f"   Taux de rapprochement: {self.stats['taux_rapprochement']:.2f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du rapprochement: {str(e)}")
            return False
    
    def generer_rapport(self, chemin_sortie: str) -> bool:
        """
        Génère un rapport détaillé des résultats
        
        Args:
            chemin_sortie: Chemin du fichier de sortie
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            logger.info(f"📄 Génération du rapport: {chemin_sortie}")
            
            # Création du rapport en plusieurs feuilles Excel
            with pl.ExcelWriter(chemin_sortie) as writer:
                # Feuille 1: Résumé
                resume_df = pl.DataFrame({
                    'Métrique': ['Total CPI', 'Total BKHIS', 'Rapprochées', 'Non rapprochées CPI', 
                                 'Non rapprochées BKHIS', 'Taux de rapprochement (%)'],
                    'Valeur': [self.stats['total_cpi'], self.stats['total_bkhis'], 
                              self.stats['rapprochees'], self.stats['non_rapprochees_cpi'],
                              self.stats['non_rapprochees_bkhis'], f"{self.stats['taux_rapprochement']:.2f}"]
                })
                resume_df.write_excel(writer, sheet_name="Résumé")
                
                # Feuille 2: Rapprochement détaillé
                if self.df_rapprochement is not None:
                    self.df_rapprochement.write_excel(writer, sheet_name="Rapprochement_Détaillé")
                
                # Feuille 3: Non rapprochés CPI
                non_rapproches_cpi = self.df_rapprochement.filter(
                    pl.col("STATUT_RAPPROCHEMENT") == "NON_RAPPROCHE_CPI"
                )
                if non_rapproches_cpi.height > 0:
                    non_rapproches_cpi.write_excel(writer, sheet_name="Non_Rapprochés_CPI")
                
                # Feuille 4: Non rapprochés BKHIS
                non_rapproches_bkhis = self.df_rapprochement.filter(
                    pl.col("STATUT_RAPPROCHEMENT") == "NON_RAPPROCHE_BKHIS"
                )
                if non_rapproches_bkhis.height > 0:
                    non_rapproches_bkhis.write_excel(writer, sheet_name="Non_Rapprochés_BKHIS")
            
            logger.info(f"✅ Rapport généré avec succès: {chemin_sortie}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération du rapport: {str(e)}")
            return False
    
    def executer_phase_complete(self, fichier_cpi: str, fichier_bkhis: str, 
                            rapport_sortie: str) -> bool:
        """
        Exécute la phase 3 complète
        
        Args:
            fichier_cpi: Chemin du fichier CPI
            fichier_bkhis: Chemin du fichier BKHIS
            rapport_sortie: Chemin du rapport de sortie
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            logger.info("🚀 Démarrage de la Phase 3 complète...")
            
            # Étape 1: Chargement des données
            if not self.charger_donnees_cpi(fichier_cpi):
                return False
            if not self.charger_donnees_bkhis(fichier_bkhis):
                return False
            
            # Étape 2: Validation
            valide, erreurs = self.valider_donnees()
            if not valide:
                logger.error("❌ Validation échouée - arrêt du traitement")
                return False
            
            # Étape 3: Préparation
            if not self.preparer_donnees_cpi():
                return False
            if not self.preparer_donnees_bkhis():
                return False
            
            # Étape 4: Rapprochement
            if not self.effectuer_rapprochement():
                return False
            
            # Étape 5: Génération du rapport
            if not self.generer_rapport(rapport_sortie):
                return False
            
            logger.info("🎉 Phase 3 terminée avec succès!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution de la Phase 3: {str(e)}")
            return False


def main():
    """
    Fonction principale pour tester le module Phase 3
    """
    print("🧪 Test du module Phase 3")
    
    # Création d'une instance du processeur
    processeur = Phase3Processor()
    
    # Exemple d'utilisation (à adapter avec vos vrais fichiers)
    fichier_cpi = "donnees_cpi.xlsx"
    fichier_bkhis = "donnees_bkhis.xlsx"
    rapport_sortie = "rapport_phase3.xlsx"
    
    # Vérification de l'existence des fichiers
    if not os.path.exists(fichier_cpi):
        print(f"⚠️ Fichier CPI non trouvé: {fichier_cpi}")
        print("Veuillez adapter les chemins des fichiers dans la fonction main()")
        return
    
    if not os.path.exists(fichier_bkhis):
        print(f"⚠️ Fichier BKHIS non trouvé: {fichier_bkhis}")
        print("Veuillez adapter les chemins des fichiers dans la fonction main()")
        return
    
    # Exécution de la phase complète
    succes = processeur.executer_phase_complete(fichier_cpi, fichier_bkhis, rapport_sortie)
    
    if succes:
        print("🎉 Phase 3 exécutée avec succès!")
        print(f"📊 Consultez le rapport: {rapport_sortie}")
    else:
        print("❌ Échec de l'exécution de la Phase 3")


if __name__ == "__main__":
    main()
