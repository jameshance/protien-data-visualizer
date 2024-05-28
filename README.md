# Mini Protein Design Dashboard

## Project Overview
The Mini Protein Design Dashboard is a web-based application designed to provide insights into protein sequences through various analytical visualizations. This tool leverages data from protein databases to display amino acid composition, hydrophobicity scores, secondary structure predictions, and more.

## Features
- **Protein Sequence Input**: Users can input or upload protein sequences to analyze.
- **Amino Acid Composition Visualization**: Displays the composition of amino acids in the protein sequence.
- **Hydrophobicity Plot**: Shows the hydrophobicity across the protein sequence.
- **Secondary Structure Prediction**: Predicts and displays the secondary structures like helices, sheets, and coils.
- **Protein Domain Information**: Integrates with Pfam and SMART to show protein domain information.
  
## Tech Stack
- **Frontend**: React.js, Chart.js for data visualization
- **Backend**: Python with Flask as the API server
- **Database**: PostgreSQL for storing protein data
- **Deployment**: Deployed on AWS

## Getting Started

### Prerequisites
Before setting up the project, ensure you have the following installed:
- Python 3.8+
- Node.js and npm
- PostgreSQL

### Installation

#### Clone the repository

```markdown
git clone https://github.com/parthasarathydNU/protien-data-visualizer.git
cd protien-data-visualizer
```

#### Set up the Backend
```bash
# Navigate to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up the database (Make sure PostgreSQL is running)
psql -U postgres -c "CREATE DATABASE protein_dashboard;"
# TODO: Write the script to set up backend
psql -U postgres -d protein_dashboard -f setup_database.sql

# Start the backend server
python app.py
```

#### Set up the Frontend
```bash
# Navigate to the frontend directory from the project root
cd ../frontend

# Install npm packages
npm install

# Start the React application
npm start
```

### Usage
1. **Open the Web Interface**: Navigate to `http://localhost:3000` in your web browser to view the dashboard.
2. **Input Protein Data**: Use the web interface to input or upload protein sequences.
3. **View Results**: Analyze the visual outputs generated by the dashboard based on the protein data provided.

## Configuration
Ensure your backend `.env` file is set up with the correct database connection details:
```env
DB_HOST=localhost
DB_USER=postgres
DB_PASS=yourpassword
DB_NAME=protein_dashboard
```

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Your Name – [Dhruv Parthasarathy](https://www.linkedin.com/in/parthadhruv/) - parthasarathy.d@northeastern.edu
Project Link: [https://github.com/parthasarathydNU/protien-data-visualizer.git](https://github.com/parthasarathydNU/protien-data-visualizer.git)

## Acknowledgements
- [UniProt](https://www.uniprot.org)
- [Pfam](https://pfam.xfam.org/)
- [SMART](http://smart.embl.de/)
- [React.js](https://reactjs.org/)
- [Flask](https://palletsprojects.com/p/flask/)
```
