"""
CodeXam Database Models

Provides database model classes for problems, submissions, and users.
This module contains the core data models that represent the main entities
in the CodeXam platform with full CRUD operations and caching support.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from cache import (
    cached, 
    cache_leaderboard, 
    cache_user_submissions, 
    invalidate_leaderboard_cache, 
    invalidate_user_cache
)
from database import (
    DatabaseError, 
    dict_to_json, 
    get_db, 
    json_to_dict, 
    validate_difficulty, 
    validate_language, 
    validate_result
)


class Problem:
    """
    Problem model class for managing coding problems.
    
    This class handles problem creation, validation, storage, and retrieval.
    It supports multiple programming languages with function signatures and
    provides comprehensive test case management.
    
    Attributes:
        id: Unique problem identifier
        title: Problem title/name
        description: Detailed problem description
        difficulty: Problem difficulty level (Easy, Medium, Hard)
        function_signatures: Language-specific function templates
        test_cases: List of test cases with inputs and expected outputs
        sample_input: Example input for display
        sample_output: Example output for display
        created_at: Problem creation timestamp
        updated_at: Last modification timestamp
    """
    
    def __init__(
        self, 
        id: Optional[int] = None, 
        title: str = "", 
        description: str = "", 
        difficulty: str = "Easy", 
        function_signatures: Optional[Dict[str, str]] = None,
        test_cases: Optional[List[Dict[str, Any]]] = None, 
        sample_input: str = "",
        sample_output: str = "", 
        created_at: Optional[str] = None, 
        updated_at: Optional[str] = None
    ) -> None:
        """
        Initialize Problem instance.
        
        Args:
            id: Unique problem identifier
            title: Problem title/name
            description: Detailed problem description
            difficulty: Problem difficulty level
            function_signatures: Language-specific function templates
            test_cases: List of test cases with inputs and expected outputs
            sample_input: Example input for display
            sample_output: Example output for display
            created_at: Problem creation timestamp
            updated_at: Last modification timestamp
        """
        self.id = id
        self.title = title.strip()
        self.description = description.strip()
        self.difficulty = difficulty
        self.function_signatures = function_signatures or {}
        self.test_cases = test_cases or []
        self.sample_input = sample_input.strip()
        self.sample_output = sample_output.strip()
        self.created_at = created_at
        self.updated_at = updated_at
    
    def validate(self) -> bool:
        """
        Validate problem data for consistency and completeness with enhanced checks.
        
        Returns:
            True if validation passes
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        # Title validation
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Problem title cannot be empty")
        
        if len(self.title) > 200:
            raise ValueError("Problem title cannot exceed 200 characters")
        
        # Check for potentially problematic characters in title
        invalid_chars = ['<', '>', '"', "'", '&']
        if any(char in self.title for char in invalid_chars):
            raise ValueError("Problem title contains invalid characters")
        
        # Description validation
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Problem description cannot be empty")
        
        if len(self.description) > 10000:
            raise ValueError("Problem description cannot exceed 10,000 characters")
        
        # Difficulty validation
        if not validate_difficulty(self.difficulty):
            raise ValueError(
                f"Invalid difficulty: {self.difficulty}. "
                f"Must be one of: Easy, Medium, Hard"
            )
        
        # Function signatures validation
        if not self.function_signatures:
            raise ValueError("At least one function signature is required")
        
        if not isinstance(self.function_signatures, dict):
            raise ValueError("Function signatures must be a dictionary")
        
        # Validate each function signature
        supported_languages = ['python', 'javascript', 'java', 'cpp']
        for lang, signature in self.function_signatures.items():
            if lang not in supported_languages:
                raise ValueError(f"Unsupported language: {lang}")
            
            if not signature or not signature.strip():
                raise ValueError(f"Function signature for {lang} cannot be empty")
            
            if len(signature) > 1000:
                raise ValueError(f"Function signature for {lang} is too long")
        
        # Test cases validation
        if not self.test_cases:
            raise ValueError("At least one test case is required")
        
        if not isinstance(self.test_cases, list):
            raise ValueError("Test cases must be a list")
        
        if len(self.test_cases) > 100:
            raise ValueError("Too many test cases (maximum 100 allowed)")
        
        # Validate test cases structure
        for i, test_case in enumerate(self.test_cases):
            if not isinstance(test_case, dict):
                raise ValueError(f"Test case {i+1} must be a dictionary")
            
            required_keys = ['input', 'expected_output']
            for key in required_keys:
                if key not in test_case:
                    raise ValueError(
                        f"Test case {i+1} missing required key: {key}"
                    )
            
            # Validate test case data size
            input_str = str(test_case['input'])
            output_str = str(test_case['expected_output'])
            
            if len(input_str) > 1000:
                raise ValueError(f"Test case {i+1} input is too large")
            
            if len(output_str) > 1000:
                raise ValueError(f"Test case {i+1} expected output is too large")
        
        return True
    
    @classmethod
    def create(
        cls, 
        title: str, 
        description: str, 
        difficulty: str,
        function_signatures: Dict[str, str], 
        test_cases: List[Dict[str, Any]],
        sample_input: str = "", 
        sample_output: str = ""
    ) -> 'Problem':
        """
        Create and save a new problem to the database.
        
        Args:
            title: Problem title/name
            description: Detailed problem description
            difficulty: Problem difficulty level (Easy, Medium, Hard)
            function_signatures: Language-specific function templates
            test_cases: List of test cases with inputs and expected outputs
            sample_input: Example input for display
            sample_output: Example output for display
            
        Returns:
            Created and saved Problem instance
            
        Raises:
            ValueError: If validation fails
            DatabaseError: If database operation fails
        """
        problem = cls(
            title=title,
            description=description,
            difficulty=difficulty,
            function_signatures=function_signatures,
            test_cases=test_cases,
            sample_input=sample_input,
            sample_output=sample_output
        )
        return problem.save()
    
    def save(self) -> 'Problem':
        """
        Save problem to database (insert or update).
        
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If validation fails
            DatabaseError: If database operation fails
        """
        self.validate()
        db = get_db()
        
        try:
            if self.id is None:
                # Insert new problem
                query = """
                INSERT INTO problems (
                    title, description, difficulty, function_signatures, 
                    test_cases, sample_input, sample_output
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.title, 
                    self.description, 
                    self.difficulty,
                    dict_to_json(self.function_signatures),
                    dict_to_json(self.test_cases),
                    self.sample_input, 
                    self.sample_output
                )
                self.id = db.execute_insert(query, params)
            else:
                # Update existing problem
                query = """
                UPDATE problems 
                SET title = ?, description = ?, difficulty = ?, 
                    function_signatures = ?, test_cases = ?, 
                    sample_input = ?, sample_output = ?
                WHERE id = ?
                """
                params = (
                    self.title, 
                    self.description, 
                    self.difficulty,
                    dict_to_json(self.function_signatures),
                    dict_to_json(self.test_cases),
                    self.sample_input, 
                    self.sample_output, 
                    self.id
                )
                db.execute_update(query, params)
            
            return self
        except Exception as e:
            raise DatabaseError(f"Failed to save problem: {e}")
    
    @classmethod
    @cached(ttl=600, key_func=lambda cls, problem_id: f"problem:{problem_id}")
    def get_by_id(cls, problem_id: int) -> Optional['Problem']:
        """
        Get problem by ID with caching support.
        
        Args:
            problem_id: Unique problem identifier
            
        Returns:
            Problem instance if found, None otherwise
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            query = "SELECT * FROM problems WHERE id = ?"
            row = db.execute_single(query, (problem_id,))
            if row:
                return cls.from_row(row)
            return None
        except Exception as e:
            raise DatabaseError(f"Failed to get problem: {e}")
    
    @classmethod
    def get_all(cls, difficulty: Optional[str] = None) -> List['Problem']:
        """
        Get all problems with optional difficulty filter.
        
        Args:
            difficulty: Optional difficulty filter (Easy, Medium, Hard)
            
        Returns:
            List of Problem instances matching the criteria
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            if difficulty and validate_difficulty(difficulty):
                query = "SELECT * FROM problems WHERE difficulty = ? ORDER BY title"
                rows = db.execute_query(query, (difficulty,))
            else:
                query = "SELECT * FROM problems ORDER BY difficulty, title"
                rows = db.execute_query(query)
            
            return [cls.from_row(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to get problems: {e}")
    
    @classmethod
    def from_row(cls, row: Any) -> 'Problem':
        """
        Create Problem instance from database row.
        
        Args:
            row: Database row with problem data
            
        Returns:
            Problem instance created from row data
        """
        return cls(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            difficulty=row['difficulty'],
            function_signatures=json_to_dict(row['function_signatures']),
            test_cases=json_to_dict(row['test_cases']),
            sample_input=row['sample_input'] or '',
            sample_output=row['sample_output'] or '',
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def __str__(self) -> str:
        """Return string representation of Problem instance."""
        return (
            f"Problem(id={self.id}, title='{self.title}', "
            f"difficulty='{self.difficulty}')"
        )
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"Problem(id={self.id}, title='{self.title}', "
            f"difficulty='{self.difficulty}', "
            f"test_cases={len(self.test_cases)})"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for this problem.
        
        Returns:
            Dictionary containing problem statistics
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            # Get submission statistics
            stats_query = """
            SELECT 
                COUNT(*) as total_submissions,
                COUNT(CASE WHEN result = 'PASS' THEN 1 END) as successful_submissions,
                COUNT(DISTINCT user_name) as unique_users,
                AVG(execution_time) as avg_execution_time,
                MIN(execution_time) as min_execution_time,
                MAX(execution_time) as max_execution_time
            FROM submissions 
            WHERE problem_id = ?
            """
            stats_row = db.execute_single(stats_query, (self.id,))
            
            # Get language distribution
            lang_query = """
            SELECT language, COUNT(*) as count
            FROM submissions 
            WHERE problem_id = ?
            GROUP BY language
            ORDER BY count DESC
            """
            lang_stats = db.execute_query(lang_query, (self.id,))
            
            # Calculate success rate
            total_subs = stats_row['total_submissions'] or 0
            successful_subs = stats_row['successful_submissions'] or 0
            success_rate = (successful_subs / total_subs * 100) if total_subs > 0 else 0
            
            return {
                'total_submissions': total_subs,
                'successful_submissions': successful_subs,
                'unique_users': stats_row['unique_users'] or 0,
                'success_rate': round(success_rate, 1),
                'avg_execution_time': stats_row['avg_execution_time'] or 0,
                'min_execution_time': stats_row['min_execution_time'] or 0,
                'max_execution_time': stats_row['max_execution_time'] or 0,
                'language_distribution': [dict(row) for row in lang_stats],
                'difficulty': self.difficulty,
                'test_cases_count': len(self.test_cases)
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get problem statistics: {e}")
    
    def get_recent_submissions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent submissions for this problem.
        
        Args:
            limit: Maximum number of submissions to return
            
        Returns:
            List of recent submission dictionaries
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            query = """
            SELECT user_name, language, result, execution_time, submitted_at
            FROM submissions 
            WHERE problem_id = ?
            ORDER BY submitted_at DESC
            LIMIT ?
            """
            rows = db.execute_query(query, (self.id, limit))
            
            return [
                {
                    'user_name': row['user_name'],
                    'language': row['language'],
                    'result': row['result'],
                    'execution_time': row['execution_time'],
                    'submitted_at': row['submitted_at']
                }
                for row in rows
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to get recent submissions: {e}")
    
    def is_solved_by_user(self, user_name: str) -> bool:
        """
        Check if this problem has been solved by a specific user.
        
        Args:
            user_name: Name of the user to check
            
        Returns:
            True if user has solved this problem, False otherwise
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            query = """
            SELECT COUNT(*) as count
            FROM submissions 
            WHERE problem_id = ? AND user_name = ? AND result = 'PASS'
            """
            result = db.execute_single(query, (self.id, user_name))
            return (result['count'] or 0) > 0
        except Exception as e:
            raise DatabaseError(f"Failed to check if problem is solved: {e}")
    
    @classmethod
    def search(
        cls, 
        query: str, 
        difficulty: Optional[str] = None,
        limit: int = 50
    ) -> List['Problem']:
        """
        Search problems by title or description.
        
        Args:
            query: Search query string
            difficulty: Optional difficulty filter
            limit: Maximum number of results to return
            
        Returns:
            List of matching Problem instances
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            search_query = """
            SELECT * FROM problems 
            WHERE (title LIKE ? OR description LIKE ?)
            """
            params = [f'%{query}%', f'%{query}%']
            
            if difficulty and validate_difficulty(difficulty):
                search_query += " AND difficulty = ?"
                params.append(difficulty)
            
            search_query += " ORDER BY title LIMIT ?"
            params.append(limit)
            
            rows = db.execute_query(search_query, tuple(params))
            return [cls.from_row(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to search problems: {e}")


class Submission:
    """
    Submission model class for managing code submissions.
    
    This class handles user code submissions, execution results, and
    performance metrics. It provides comprehensive tracking of submission
    history and statistics.
    
    Attributes:
        id: Unique submission identifier
        problem_id: ID of the associated problem
        user_name: Name of the user who submitted
        language: Programming language used
        code: Submitted source code
        result: Execution result (PASS, FAIL, ERROR, TIMEOUT)
        execution_time: Time taken to execute in seconds
        memory_used: Memory consumed in bytes
        error_message: Error details if execution failed
        submitted_at: Submission timestamp
    """
    
    def __init__(
        self, 
        id: Optional[int] = None, 
        problem_id: int = 0, 
        user_name: str = "",
        language: str = "", 
        code: str = "", 
        result: str = "PENDING",
        execution_time: float = 0.0, 
        memory_used: int = 0, 
        error_message: str = "", 
        submitted_at: Optional[str] = None
    ) -> None:
        """
        Initialize Submission instance.
        
        Args:
            id: Unique submission identifier
            problem_id: ID of the associated problem
            user_name: Name of the user who submitted
            language: Programming language used
            code: Submitted source code
            result: Execution result
            execution_time: Time taken to execute in seconds
            memory_used: Memory consumed in bytes
            error_message: Error details if execution failed
            submitted_at: Submission timestamp
        """
        self.id = id
        self.problem_id = problem_id
        self.user_name = user_name.strip()
        self.language = language.lower()
        self.code = code
        self.result = result
        self.execution_time = execution_time
        self.memory_used = memory_used
        self.error_message = error_message
        self.submitted_at = submitted_at
    
    def validate(self) -> bool:
        """
        Validate submission data for consistency and completeness with enhanced checks.
        
        Returns:
            True if validation passes
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        # Problem ID validation
        if not isinstance(self.problem_id, int) or self.problem_id <= 0:
            raise ValueError("Problem ID must be a positive integer")
        
        # User name validation
        if not self.user_name or len(self.user_name.strip()) == 0:
            raise ValueError("User name cannot be empty")
        
        if len(self.user_name) > 100:
            raise ValueError("User name cannot exceed 100 characters")
        
        # Check for potentially problematic characters in user name
        invalid_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        if any(char in self.user_name for char in invalid_chars):
            raise ValueError("User name contains invalid characters")
        
        # Language validation
        if not validate_language(self.language):
            supported_langs = ['python', 'javascript', 'java', 'cpp']
            raise ValueError(
                f"Unsupported language: {self.language}. "
                f"Supported languages: {', '.join(supported_langs)}"
            )
        
        # Code validation
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("Code cannot be empty")
        
        if len(self.code) > 100000:  # 100KB limit (increased for complex solutions)
            raise ValueError("Code exceeds maximum length limit (100KB)")
        
        # Check for potentially dangerous code patterns
        dangerous_patterns = ['__import__', 'eval(', 'exec(', 'open(', 'file(']
        code_lower = self.code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                raise ValueError(f"Code contains restricted pattern: {pattern}")
        
        # Result validation
        if not validate_result(self.result):
            valid_results = ['PASS', 'FAIL', 'ERROR', 'TIMEOUT']
            raise ValueError(
                f"Invalid result: {self.result}. "
                f"Valid results: {', '.join(valid_results)}"
            )
        
        # Execution time validation
        if self.execution_time is not None:
            if not isinstance(self.execution_time, (int, float)):
                raise ValueError("Execution time must be a number")
            
            if self.execution_time < 0:
                raise ValueError("Execution time cannot be negative")
            
            if self.execution_time > 300:  # 5 minutes max
                raise ValueError("Execution time cannot exceed 300 seconds")
        
        # Memory usage validation
        if self.memory_used is not None:
            if not isinstance(self.memory_used, int):
                raise ValueError("Memory used must be an integer")
            
            if self.memory_used < 0:
                raise ValueError("Memory used cannot be negative")
            
            if self.memory_used > 1024 * 1024 * 1024:  # 1GB max
                raise ValueError("Memory used cannot exceed 1GB")
        
        # Error message validation
        if self.error_message and len(self.error_message) > 5000:
            raise ValueError("Error message is too long (max 5000 characters)")
        
        return True
    
    @classmethod
    def create(
        cls, 
        problem_id: int, 
        user_name: str, 
        language: str, 
        code: str,
        result: str = "PENDING", 
        execution_time: float = 0.0, 
        memory_used: int = 0, 
        error_message: str = ""
    ) -> 'Submission':
        """
        Create and save a new submission to the database.
        
        Args:
            problem_id: ID of the associated problem
            user_name: Name of the user who submitted
            language: Programming language used
            code: Submitted source code
            result: Execution result
            execution_time: Time taken to execute in seconds
            memory_used: Memory consumed in bytes
            error_message: Error details if execution failed
            
        Returns:
            Created and saved Submission instance
            
        Raises:
            ValueError: If validation fails
            DatabaseError: If database operation fails
        """
        submission = cls(
            problem_id=problem_id, 
            user_name=user_name, 
            language=language,
            code=code, 
            result=result, 
            execution_time=execution_time,
            memory_used=memory_used, 
            error_message=error_message
        )
        return submission.save()
    
    def save(self) -> 'Submission':
        """
        Save submission to database (insert or update).
        
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If validation fails
            DatabaseError: If database operation fails
        """
        self.validate()
        db = get_db()
        
        try:
            if self.id is None:
                # Insert new submission
                query = """
                INSERT INTO submissions (
                    problem_id, user_name, language, code, result,
                    execution_time, memory_used, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.problem_id, 
                    self.user_name, 
                    self.language, 
                    self.code,
                    self.result, 
                    self.execution_time, 
                    self.memory_used, 
                    self.error_message
                )
                self.id = db.execute_insert(query, params)
                
                # Invalidate relevant caches
                invalidate_user_cache(self.user_name)
                invalidate_leaderboard_cache()
                
            else:
                # Update existing submission
                query = """
                UPDATE submissions 
                SET problem_id = ?, user_name = ?, language = ?, code = ?, 
                    result = ?, execution_time = ?, memory_used = ?, 
                    error_message = ?
                WHERE id = ?
                """
                params = (
                    self.problem_id, 
                    self.user_name, 
                    self.language, 
                    self.code,
                    self.result, 
                    self.execution_time, 
                    self.memory_used, 
                    self.error_message, 
                    self.id
                )
                db.execute_update(query, params)
                
                # Invalidate relevant caches
                invalidate_user_cache(self.user_name)
                invalidate_leaderboard_cache()
            
            return self
        except Exception as e:
            raise DatabaseError(f"Failed to save submission: {e}")
    
    @classmethod
    def get_by_id(cls, submission_id: int) -> Optional['Submission']:
        """
        Get submission by ID.
        
        Args:
            submission_id: Unique submission identifier
            
        Returns:
            Submission instance if found, None otherwise
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            query = "SELECT * FROM submissions WHERE id = ?"
            row = db.execute_single(query, (submission_id,))
            if row:
                return cls.from_row(row)
            return None
        except Exception as e:
            raise DatabaseError(f"Failed to get submission: {e}")
    
    @classmethod
    @cached(
        ttl=60, 
        key_func=lambda cls, user_name, limit=50: f"user_submissions:{user_name}:{limit}"
    )
    def get_by_user(
        cls, 
        user_name: str, 
        limit: Optional[int] = None
    ) -> List['Submission']:
        """
        Get submissions by user with caching support.
        
        Args:
            user_name: Name of the user
            limit: Maximum number of submissions to return
            
        Returns:
            List of Submission instances for the user
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            query = ("SELECT * FROM submissions WHERE user_name = ? "
                    "ORDER BY submitted_at DESC")
            params = [user_name]
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            rows = db.execute_query(query, tuple(params))
            return [cls.from_row(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to get user submissions: {e}")
    
    @classmethod
    def get_by_user_and_problem(
        cls, 
        user_name: str, 
        problem_id: int, 
        limit: Optional[int] = 5
    ) -> List['Submission']:
        """
        Get submissions by user for a specific problem (optimized query).
        
        Args:
            user_name: Name of the user
            problem_id: ID of the specific problem
            limit: Maximum number of submissions to return
            
        Returns:
            List of Submission instances for the user and problem
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            query = """
            SELECT * FROM submissions 
            WHERE user_name = ? AND problem_id = ? 
            ORDER BY submitted_at DESC
            LIMIT ?
            """
            rows = db.execute_query(query, (user_name, problem_id, limit))
            return [cls.from_row(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to get user submissions for problem: {e}")
    
    @classmethod
    @cached(ttl=120, key_func=lambda cls, limit=50: f"leaderboard:{limit}")
    def get_leaderboard(cls, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get leaderboard data based on problems solved with caching.
        
        Args:
            limit: Maximum number of users to include in leaderboard
            
        Returns:
            List of dictionaries containing leaderboard data with ranks
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            query = """
            SELECT 
                user_name,
                COUNT(DISTINCT CASE WHEN result = 'PASS' THEN problem_id END) 
                    as problems_solved,
                COUNT(*) as total_submissions
            FROM submissions 
            GROUP BY user_name
            ORDER BY problems_solved DESC, total_submissions ASC
            LIMIT ?
            """
            
            rows = db.execute_query(query, (limit,))
            leaderboard = []
            for i, row in enumerate(rows):
                leaderboard.append({
                    'rank': i + 1,
                    'user_name': row['user_name'],
                    'problems_solved': row['problems_solved'],
                    'total_submissions': row['total_submissions']
                })
            
            return leaderboard
        except Exception as e:
            raise DatabaseError(f"Failed to get leaderboard: {e}")
    
    @classmethod
    def from_row(cls, row: Any) -> 'Submission':
        """
        Create Submission instance from database row.
        
        Args:
            row: Database row with submission data
            
        Returns:
            Submission instance created from row data
        """
        return cls(
            id=row['id'],
            problem_id=row['problem_id'],
            user_name=row['user_name'],
            language=row['language'],
            code=row['code'],
            result=row['result'],
            execution_time=row['execution_time'] or 0.0,
            memory_used=row['memory_used'] or 0,
            error_message=row['error_message'] or '',
            submitted_at=row['submitted_at']
        )
    
    def __str__(self) -> str:
        """Return string representation of Submission instance."""
        return (
            f"Submission(id={self.id}, problem_id={self.problem_id}, "
            f"user='{self.user_name}', result='{self.result}')"
        )
    
    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"Submission(id={self.id}, problem_id={self.problem_id}, "
            f"user='{self.user_name}', language='{self.language}', "
            f"result='{self.result}', execution_time={self.execution_time})"
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this submission.
        
        Returns:
            Dictionary containing performance metrics and analysis
        """
        metrics = {
            'execution_time': self.execution_time or 0,
            'memory_used': self.memory_used or 0,
            'result': self.result,
            'language': self.language,
            'code_length': len(self.code),
            'performance_score': 0
        }
        
        # Calculate performance score (0-100)
        if self.result == 'PASS':
            base_score = 100
            
            # Deduct points for execution time (assuming 5s is max)
            if self.execution_time:
                time_penalty = min((self.execution_time / 5.0) * 20, 20)
                base_score -= time_penalty
            
            # Deduct points for memory usage (assuming 128MB is max)
            if self.memory_used:
                memory_penalty = min((self.memory_used / (128 * 1024 * 1024)) * 20, 20)
                base_score -= memory_penalty
            
            # Bonus for concise code (up to 10 points)
            if len(self.code) < 200:
                base_score += 10
            elif len(self.code) < 500:
                base_score += 5
            
            metrics['performance_score'] = max(int(base_score), 0)
        
        return metrics
    
    def get_code_analysis(self) -> Dict[str, Any]:
        """
        Analyze the submitted code for various metrics.
        
        Returns:
            Dictionary containing code analysis results
        """
        analysis = {
            'language': self.language,
            'code_length': len(self.code),
            'line_count': len(self.code.split('\n')),
            'complexity_indicators': {},
            'patterns': []
        }
        
        code_lower = self.code.lower()
        
        # Language-specific analysis
        if self.language == 'python':
            analysis['complexity_indicators'] = {
                'loops': code_lower.count('for ') + code_lower.count('while '),
                'conditionals': code_lower.count('if ') + code_lower.count('elif '),
                'functions': code_lower.count('def '),
                'imports': code_lower.count('import ') + code_lower.count('from ')
            }
            
            # Common patterns
            if 'dict' in code_lower or '{' in self.code:
                analysis['patterns'].append('uses_dictionary')
            if 'list' in code_lower or '[' in self.code:
                analysis['patterns'].append('uses_list')
            if 'set(' in code_lower:
                analysis['patterns'].append('uses_set')
            if 'sorted(' in code_lower:
                analysis['patterns'].append('uses_sorting')
        
        elif self.language == 'javascript':
            analysis['complexity_indicators'] = {
                'loops': code_lower.count('for ') + code_lower.count('while '),
                'conditionals': code_lower.count('if ') + code_lower.count('else if'),
                'functions': code_lower.count('function ') + code_lower.count('=>'),
                'objects': code_lower.count('{')
            }
        
        return analysis
    
    @classmethod
    def get_user_statistics(cls, user_name: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a specific user.
        
        Args:
            user_name: Name of the user
            
        Returns:
            Dictionary containing user statistics
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            # Basic statistics
            basic_query = """
            SELECT 
                COUNT(*) as total_submissions,
                COUNT(CASE WHEN result = 'PASS' THEN 1 END) as successful_submissions,
                COUNT(DISTINCT problem_id) as problems_attempted,
                COUNT(DISTINCT CASE WHEN result = 'PASS' THEN problem_id END) as problems_solved,
                AVG(execution_time) as avg_execution_time,
                MIN(submitted_at) as first_submission,
                MAX(submitted_at) as last_submission
            FROM submissions 
            WHERE user_name = ?
            """
            basic_stats = db.execute_single(basic_query, (user_name,))
            
            # Language distribution
            lang_query = """
            SELECT language, 
                   COUNT(*) as total,
                   COUNT(CASE WHEN result = 'PASS' THEN 1 END) as successful
            FROM submissions 
            WHERE user_name = ?
            GROUP BY language
            ORDER BY total DESC
            """
            lang_stats = db.execute_query(lang_query, (user_name,))
            
            # Difficulty distribution
            diff_query = """
            SELECT p.difficulty,
                   COUNT(*) as attempted,
                   COUNT(CASE WHEN s.result = 'PASS' THEN 1 END) as solved
            FROM submissions s
            JOIN problems p ON s.problem_id = p.id
            WHERE s.user_name = ?
            GROUP BY p.difficulty
            """
            diff_stats = db.execute_query(diff_query, (user_name,))
            
            # Calculate success rate
            total_subs = basic_stats['total_submissions'] or 0
            successful_subs = basic_stats['successful_submissions'] or 0
            success_rate = (successful_subs / total_subs * 100) if total_subs > 0 else 0
            
            return {
                'user_name': user_name,
                'total_submissions': total_subs,
                'successful_submissions': successful_subs,
                'problems_attempted': basic_stats['problems_attempted'] or 0,
                'problems_solved': basic_stats['problems_solved'] or 0,
                'success_rate': round(success_rate, 1),
                'avg_execution_time': basic_stats['avg_execution_time'] or 0,
                'first_submission': basic_stats['first_submission'],
                'last_submission': basic_stats['last_submission'],
                'language_stats': [dict(row) for row in lang_stats],
                'difficulty_stats': [dict(row) for row in diff_stats]
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get user statistics: {e}")
    
    @classmethod
    def get_trending_problems(cls, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending problems based on recent submission activity.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of problems to return
            
        Returns:
            List of trending problem dictionaries
            
        Raises:
            DatabaseError: If database operation fails
        """
        db = get_db()
        try:
            query = """
            SELECT p.id, p.title, p.difficulty,
                   COUNT(s.id) as recent_submissions,
                   COUNT(DISTINCT s.user_name) as unique_users,
                   COUNT(CASE WHEN s.result = 'PASS' THEN 1 END) as successful_submissions
            FROM problems p
            JOIN submissions s ON p.id = s.problem_id
            WHERE s.submitted_at >= datetime('now', '-{} days')
            GROUP BY p.id, p.title, p.difficulty
            ORDER BY recent_submissions DESC, unique_users DESC
            LIMIT ?
            """.format(days)
            
            rows = db.execute_query(query, (limit,))
            
            return [
                {
                    'problem_id': row['id'],
                    'title': row['title'],
                    'difficulty': row['difficulty'],
                    'recent_submissions': row['recent_submissions'],
                    'unique_users': row['unique_users'],
                    'successful_submissions': row['successful_submissions'],
                    'success_rate': round(
                        (row['successful_submissions'] / row['recent_submissions'] * 100)
                        if row['recent_submissions'] > 0 else 0, 1
                    )
                }
                for row in rows
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to get trending problems: {e}")


def main() -> None:
    """Main function for testing models functionality."""
    print("🧪 Testing models...")
    try:
        # Test basic functionality
        print("✅ Models loaded successfully!")
        
        # Test Problem model
        test_problem = Problem(
            title="Test Problem",
            description="Test description",
            difficulty="Easy",
            function_signatures={"python": "def solution(): pass"},
            test_cases=[{"input": [], "expected_output": "test"}]
        )
        print(f"✅ Problem model test: {test_problem}")
        
        # Test Submission model
        test_submission = Submission(
            problem_id=1,
            user_name="test_user",
            language="python",
            code="def solution(): return 'test'",
            result="PASS"
        )
        print(f"✅ Submission model test: {test_submission}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()