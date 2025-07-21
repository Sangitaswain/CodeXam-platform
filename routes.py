"""
CodeXam Web Routes
URL routing and view logic for the CodeXam platform
"""

from flask import render_template, request, jsonify, session, redirect, url_for, flash
from models import Problem, Submission
from database import get_platform_stats
import logging

logger = logging.getLogger(__name__)

def register_routes(app):
    """Register all routes with the Flask application."""
    
    @app.route('/')
    def index():
        """Landing page route with platform introduction and statistics."""
        try:
            stats = get_platform_stats()
            logger.info("Landing page accessed")
            return render_template('index.html', stats=stats)
        except Exception as e:
            logger.error(f"Error loading landing page: {e}")
            # Fallback stats if database is not available
            stats = {
                'total_problems': 0,
                'total_submissions': 0,
                'total_users': 0,
                'last_updated': 'N/A'
            }
            return render_template('index.html', stats=stats)
    
    @app.route('/problems')
    def problems_list():
        """Problems list route displaying all available problems."""
        try:
            difficulty_filter = request.args.get('difficulty')
            problems = Problem.get_all(difficulty=difficulty_filter)
            
            logger.info(f"Problems list accessed, showing {len(problems)} problems")
            return render_template('problems.html', 
                                 problems=problems, 
                                 current_filter=difficulty_filter)
        except Exception as e:
            logger.error(f"Error loading problems list: {e}")
            flash('Error loading problems. Please try again.', 'error')
            return render_template('problems.html', problems=[], current_filter=None)
    
    @app.route('/problem/<int:problem_id>')
    def problem_detail(problem_id):
        """Problem detail route showing complete problem description and editor."""
        try:
            problem = Problem.get_by_id(problem_id)
            if not problem:
                flash('Problem not found.', 'error')
                return redirect(url_for('problems_list'))
            
            # Get user's previous submissions for this problem
            user_name = session.get('user_name', 'Anonymous')
            user_submissions = []
            if user_name != 'Anonymous':
                user_submissions = Submission.get_by_user(user_name)
                user_submissions = [s for s in user_submissions if s.problem_id == problem_id]
            
            logger.info(f"Problem {problem_id} detail accessed by {user_name}")
            return render_template('problem.html', 
                                 problem=problem, 
                                 user_submissions=user_submissions)
        except Exception as e:
            logger.error(f"Error loading problem {problem_id}: {e}")
            flash('Error loading problem. Please try again.', 'error')
            return redirect(url_for('problems_list'))
    
    @app.route('/submit', methods=['POST'])
    def submit_code():
        """Code submission route for executing and evaluating user code."""
        try:
            # Get submission data
            problem_id = request.form.get('problem_id', type=int)
            code = request.form.get('code', '').strip()
            language = request.form.get('language', '').lower()
            user_name = session.get('user_name', 'Anonymous')
            
            # Validate inputs
            if not problem_id or not code or not language:
                return jsonify({
                    'result': 'ERROR',
                    'message': 'Missing required fields: problem_id, code, and language'
                }), 400
            
            # Get problem
            problem = Problem.get_by_id(problem_id)
            if not problem:
                return jsonify({
                    'result': 'ERROR',
                    'message': 'Problem not found'
                }), 404
            
            # Import judge engine
            from judge import SimpleJudge
            judge = SimpleJudge()
            
            # Execute code
            result = judge.execute_code(language, code, problem.test_cases)
            
            # Store submission
            submission = Submission.create(
                problem_id=problem_id,
                user_name=user_name,
                language=language,
                code=code,
                result=result['result'],
                execution_time=result.get('execution_time', 0.0),
                memory_used=result.get('memory_used', 0),
                error_message=result.get('message', '')
            )
            
            logger.info(f"Code submitted by {user_name} for problem {problem_id}: {result['result']}")
            
            return jsonify({
                'result': result['result'],
                'message': result['message'],
                'execution_time': result.get('execution_time', 0.0),
                'submission_id': submission.id
            })
            
        except Exception as e:
            logger.error(f"Error processing code submission: {e}")
            return jsonify({
                'result': 'ERROR',
                'message': f'Submission failed: {str(e)}'
            }), 500
    
    @app.route('/submissions')
    def submissions_history():
        """Submission history route showing user's past attempts."""
        try:
            user_name = session.get('user_name', 'Anonymous')
            if user_name == 'Anonymous':
                flash('Please set your name to view submission history.', 'info')
                return redirect(url_for('set_name'))
            
            submissions = Submission.get_by_user(user_name, limit=50)
            
            logger.info(f"Submission history accessed by {user_name}")
            return render_template('submissions.html', 
                                 submissions=submissions, 
                                 user_name=user_name)
        except Exception as e:
            logger.error(f"Error loading submission history: {e}")
            flash('Error loading submission history. Please try again.', 'error')
            return render_template('submissions.html', submissions=[], user_name='')
    
    @app.route('/leaderboard')
    def leaderboard():
        """Leaderboard route showing user rankings by problems solved."""
        try:
            leaderboard_data = Submission.get_leaderboard(limit=50)
            
            logger.info("Leaderboard accessed")
            return render_template('leaderboard.html', leaderboard=leaderboard_data)
        except Exception as e:
            logger.error(f"Error loading leaderboard: {e}")
            flash('Error loading leaderboard. Please try again.', 'error')
            return render_template('leaderboard.html', leaderboard=[])
    
    @app.route('/set_name', methods=['GET', 'POST'])
    def set_name():
        """User identification route for setting display name."""
        if request.method == 'POST':
            user_name = request.form.get('user_name', '').strip()
            if user_name:
                session['user_name'] = user_name
                flash(f'Welcome, {user_name}!', 'success')
                logger.info(f"User name set: {user_name}")
                
                # Redirect to the page they came from or problems list
                next_page = request.form.get('next') or url_for('problems_list')
                return redirect(next_page)
            else:
                flash('Please enter a valid name.', 'error')
        
        # Show name setting form
        next_page = request.args.get('next', url_for('problems_list'))
        return render_template('set_name.html', next_page=next_page)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
        try:
            stats = get_platform_stats()
            return jsonify({
                'status': 'healthy',
                'message': 'CodeXam is running',
                'database': 'connected',
                'stats': stats
            })
        except Exception as e:
            return jsonify({
                'status': 'degraded',
                'message': 'CodeXam is running with issues',
                'database': 'error',
                'error': str(e)
            }), 500

    logger.info("All routes registered successfully")