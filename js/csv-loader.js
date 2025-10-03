// CSV to JSON converter for extracted features
function parseCSVToJSON(csvText) {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',');
    const papers = [];
    
    console.log('CSV Headers:', headers);
    console.log('Total lines:', lines.length);
    
    for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);
        if (values.length === 0) continue;
        
        console.log(`Processing paper ${i}:`, values[2]); // Log title
        
        const paper = {
            id: `paper_${String(i).padStart(3, '0')}`,
            title: values[2] || 'Untitled',
            title_verbatim: values[3] || '',
            authors: values[0] ? values[0].split(';').map(a => a.trim()) : [],
            authors_verbatim: values[1] || '',
            journal: values[4] || '',
            journal_verbatim: values[5] || '',
            year: parseInt(values[6]) || new Date().getFullYear(),
            citation: values[7] || '',
            abstract: values[8] || '',
            abstract_verbatim: values[9] || '',
            sample_size: parseInt(values[36]) || 0,
            countries: values[38] ? [values[38]] : ['USA'], // Fixed index
            methodology: values[18] || 'Unknown',
            research_type: 'Experimental Research',
            citations: 0,
            impact_factor: 0,
            keywords: ['social media', 'politics'],
            extracted_features: {
                independent_variables: values[10] || '',
                independent_variables_verbatim: values[11] || '',
                dependent_variables: values[12] || '',
                dependent_variables_verbatim: values[13] || '',
                survey_questions: values[14] || '',
                survey_questions_verbatim: values[15] || '',
                incentive: values[16] || '',
                incentive_verbatim: values[17] || '',
                study_type: values[18] || '',
                study_type_verbatim: values[19] || '',
                analysis_equations: values[20] || '',
                analysis_equations_verbatim: values[21] || '',
                level_of_analysis: values[22] || '',
                level_of_analysis_verbatim: values[23] || '',
                main_effects: values[24] || '',
                main_effects_verbatim: values[25] || '',
                statistical_power: values[26] || '',
                statistical_power_verbatim: values[27] || '',
                moderators: values[28] || '',
                moderators_verbatim: values[29] || '',
                moderation_results: values[30] || '',
                moderation_results_verbatim: values[31] || '',
                demographics: values[32] || '',
                demographics_verbatim: values[33] || '',
                recruitment_source: values[34] || '',
                recruitment_source_verbatim: values[35] || '',
                sample_size: values[36] || '',
                sample_size_verbatim: values[37] || '',
                country_region: values[38] || '',
                sociocultural_context: values[39] || '',
                political_context: values[40] || '',
                platform_technological_context: values[41] || '',
                temporal_context: values[42] || '',
                recommended_moderators: values[43] || '',
                research_context: values[44] || '',
                intervention_insights: values[45] || ''
            }
        };
        
        papers.push(paper);
    }
    
    console.log('Parsed papers:', papers.length);
    return { papers };
}

// Helper function to parse CSV line handling commas within quotes
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    
    result.push(current.trim());
    return result;
}

// Load CSV data and convert to JSON
async function loadCSVData() {
    try {
        const response = await fetch('data/papers_extracted.csv');
        const csvText = await response.text();
        return parseCSVToJSON(csvText);
    } catch (error) {
        console.error('Error loading CSV data:', error);
        return { papers: [] };
    }
}

// Export for use in other files
window.csvDataLoader = {
    loadCSVData,
    parseCSVToJSON
};
