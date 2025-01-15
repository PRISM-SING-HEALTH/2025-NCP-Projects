# 2025-NCP-Projects

## Variant Database

### Overview
The Variant Database project focuses on developing a **stand-alone application** for managing, querying, and validating genetic variant data. The application is designed to run on **Windows laptops** with Python packaging.
### Project Students
- Angelo Lagahit (https://www.linkedin.com/in/angelo-lagahit/)
- Sze Wei Shong (https://www.linkedin.com/in/sze-wei-shong/)

---

### Key Features

#### 1. **Data Management**
- Harmonisation and Consolidation: Integrates variant data from multiple sources.
- Privacy Maintenance: Enables distributed access while ensuring privacy.
- Smart Distributed Storage: Efficiently manages data across three "disk locations."

#### 2. **Querying and Filtering**
- Layered Filtering:
  - Level 1: Filters by gene, phenotype, variant type, and solved status.
  - Level 2: Filters based on variant-specific information.
- Integrated Querying: Provides seamless access to relevant data.

#### 3. **Export and Validation**
- Enables results export.
- Validates exported data against external services such as VariantValidator.org

#### 4. **HPO Annotation**
- Integrates Gabrielle's work on Human Phenotype Ontology (HPO) for annotating free-text phenotypic descriptions.

---

### Specifications
- Windows-compatible stand-alone app.
- Python-based packaging.
- Manages data across multiple disk locations with distributed storage.
- Supports variant checking outside the network.
