import re
from typing import List, Dict, Tuple, Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class SkillMatcher:
    """
    Skill matching & relevance engine using TF-IDF and Cosine Similarity.
    Evaluates semantic and token alignment between:
    - Training Curriculum Skills
    - Workplace Required / Employer Feedback Skills
    """

    @staticmethod
    def _clean_skills(skills_input: Any) -> List[str]:
        """Normalizes skill inputs into a clean list of lowercase skill strings."""
        if not skills_input:
            return []
        if isinstance(skills_input, list):
            raw_list = skills_input
        elif isinstance(skills_input, str):
            # Split by commas, semicolons, newlines, or bullets
            raw_list = re.split(r'[,;\n•\r]+', skills_input)
        else:
            raw_list = [str(skills_input)]

        cleaned = []
        for s in raw_list:
            item = s.strip().lower()
            # Remove punctuation like trailing dots or quotes
            item = re.sub(r'^[^\w]+|[^\w]+$', '', item)
            if item and len(item) > 1 and item not in cleaned:
                cleaned.append(item)
        return cleaned

    @classmethod
    def calculate_relevance(cls, curriculum_skills: Any, workplace_skills: Any) -> Dict[str, Any]:
        """
        Calculates Training -> Job Relevance percentage and detailed skill gap breakdown.
        Returns:
            {
                'relevance_percentage': 78.5,
                'matched_skills': ['basic excel', 'communication', 'data entry'],
                'missing_skills': ['advanced excel', 'data analysis'],
                'curriculum_skills': [...],
                'workplace_skills': [...]
            }
        """
        curr_list = cls._clean_skills(curriculum_skills)
        work_list = cls._clean_skills(workplace_skills)

        if not curr_list or not work_list:
            return {
                'relevance_percentage': 0.0,
                'matched_skills': [],
                'missing_skills': work_list,
                'curriculum_skills': curr_list,
                'workplace_skills': work_list
            }

        # Determine exact token / substring matches
        matched = []
        missing = []

        for w_skill in work_list:
            is_match = False
            for c_skill in curr_list:
                # Direct match or partial subphrase overlap (e.g. 'excel' in 'basic excel')
                if w_skill == c_skill or (len(w_skill) > 3 and w_skill in c_skill) or (len(c_skill) > 3 and c_skill in w_skill):
                    is_match = True
                    break
            if is_match:
                matched.append(w_skill)
            else:
                missing.append(w_skill)

        # Mathematical TF-IDF + Cosine Similarity computation
        if SKLEARN_AVAILABLE:
            curr_text = " ".join(curr_list)
            work_text = " ".join(work_list)
            try:
                vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b', ngram_range=(1, 2))
                tfidf_matrix = vectorizer.fit_transform([curr_text, work_text])
                cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                # Combined score: 60% cosine similarity + 40% discrete token overlap ratio
                token_ratio = len(matched) / max(len(work_list), 1)
                combined_score = round(((cos_sim * 0.6) + (token_ratio * 0.4)) * 100, 1)
            except Exception:
                combined_score = round((len(matched) / max(len(work_list), 1)) * 100, 1)
        else:
            # Deterministic fallback when scikit-learn wheel is compiling or not present
            combined_score = round((len(matched) / max(len(work_list), 1)) * 100, 1)

        # Bound score between 0 and 100
        combined_score = max(0.0, min(100.0, combined_score))

        return {
            'relevance_percentage': combined_score,
            'matched_skills': matched,
            'missing_skills': missing,
            'curriculum_skills': curr_list,
            'workplace_skills': work_list
        }
