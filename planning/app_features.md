---

## Feature Set: VeraDose App

### Pillar 1: Prescription Safety Check (The Original Core)

| Feature | Description |
| :--- | :--- |
| **Prescription OCR Scan** | User takes a photo of the handwritten or printed prescription. App extracts drug name, dosage, frequency, and duration using optical character recognition optimized for varied handwriting and low-quality paper. |
| **Manual Entry Fallback** | For users with feature phones or poor camera quality, a simple text-based entry system allows manual input of drug details. |
| **Dosage Verification** | Compares prescribed dose against weight-based and age-based safe therapeutic ranges using a curated, offline-first drug database tailored to common medications in the target region. |
| **Drug-Drug Interaction Check** | Cross-references new medication against the patient's existing medication list (manually entered or previously scanned) to flag potentially dangerous combinations. |
| **Allergy Alert** | Flags any medication that contains a known allergen previously recorded by the user. |
| **Clear, Localized Output** | Instead of technical warnings, the app displays simple, actionable messages in the user's preferred language: *"This dose may be high for a child of this weight. Confirm with pharmacist."* |

---

### Pillar 2: Adherence Tracking & Reminders (Your Addition)

This pillar addresses the reality that even a correctly prescribed medication is ineffective if not taken correctly. For elderly patients, forgetfulness, polypharmacy, and lack of a caregiver can lead to missed doses, double doses, or dangerous timing errors.

| Feature | Description |
| :--- | :--- |
| **Medication Schedule Creation** | After a prescription is verified, the app automatically generates a personalized schedule based on frequency (e.g., "twice daily," "every 8 hours"). User can adjust times to match their routine. |
| **Customizable Reminders** | Push notifications at scheduled times. Designed with elderly users in mind: large text, high-contrast colors, and optional loud audible alerts. Supports multiple languages. |
| **"Did You Take It?" Confirmation** | When a reminder fires, the user taps a simple **"Taken"** or **"Skip"** button. If no response after 30 minutes, a follow-up reminder is sent. |
| **Missed Dose Handling** | If a dose is missed, the app provides clear guidance: *"You missed your evening dose. If it has been less than 2 hours, take it now. Otherwise, skip and take next dose as scheduled. Do not double."* |
| **Double-Dose Prevention** | If the user attempts to mark a dose as taken outside the scheduled window, the app checks the last recorded dose. If the time gap is too short, it displays: *"You already took this medication [X] hours ago. Are you sure?"* |
| **Family/Caregiver Sharing (Optional)** | For elderly patients with family caregivers, the app can send a daily summary or real-time alerts to a trusted family member's phone (e.g., "Mom missed her morning blood pressure medication"). No smartphone required on the patient's end if using a basic version with SMS fallback. |

---

### Pillar 3: Medication History & Health Log

This pillar transforms the app from a transactional tool into a longitudinal health record. For elderly patients who see multiple providers, this feature fills the gap left by the absence of centralized electronic medical records.

| Feature | Description |
| :--- | :--- |
| **Active Medication List** | A simple, always-visible list of all current medications, dosages, and schedules. Serves as a single source of truth for the patient, family, and any new clinician. |
| **Adherence History Calendar** | Visual calendar showing days when medication was taken, missed, or skipped. Color-coded for quick understanding. Elderly users or caregivers can show this to a doctor to assess adherence patterns. |
| **"Last Taken" Indicator** | For each medication, the app displays: *"Last taken: [date] at [time]"* directly on the home screen. Solves the problem of a patient asking *"Did I already take my morning pill?"* |
| **Medication Timeline View** | A chronological log showing exactly when each dose was confirmed taken. Critical for investigating adverse events or determining if an overdose occurred. |
| **Exportable History** | Ability to generate a simple, printable summary (via SMS, WhatsApp, or PDF) that the patient can bring to clinic visits. Ensures the clinician has accurate information even without electronic records. |
| **Reconciliation Assistant** | When a new prescription is added, the app prompts: *"You are currently taking [Drug X]. Would you like to stop this, or is this an additional medication?"* Helps prevent unintentional continuation of medications that were meant to be discontinued. |

---

---

## Summary: Feature Architecture

| Pillar | Core Features | Problem Solved |
| :--- | :--- | :--- |
| **Safety Check** | OCR scan, dosage verification, drug-drug interaction, allergy alert | Catching prescription errors at the point of dispensing |
| **Adherence Tracking** | Reminders, "Taken" confirmation, missed dose guidance, double-dose prevention | Ensuring correct timing and preventing accidental double-dosing |
| **Health History** | Active medication list, adherence calendar, "last taken" indicator, exportable summary | Giving patients and clinicians a complete picture; solving "did I take it?" |
| **Accessibility** | Offline mode, SMS fallback, voice interface, elderly-friendly UI, multi-language | Ensuring usability in low-resource settings and for vulnerable populations |

---
