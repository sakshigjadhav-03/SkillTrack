from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify

def login_required(f):
    """Decorator ensuring that a user is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator restricting access to specific user roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            user_role = session.get('role')
            if user_role not in roles:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'error': 'Access forbidden: unauthorized role'}), 403
                flash('You do not have permission to view this section.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    """Returns the current user details from the session if logged in."""
    if 'user_id' in session:
        return {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role'),
            'email': session.get('email'),
            'trainee_id': session.get('trainee_id'),
            'outcome_id': session.get('outcome_id'),
            'employer_id': session.get('employer_id'),
            'provider_id': session.get('provider_id')
        }
    return None
