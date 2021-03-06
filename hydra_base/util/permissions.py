#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) Copyright 2013 to 2017 University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>
#

from .. import db
from ..db.model import Perm, User, RolePerm, RoleUser
from sqlalchemy.orm.exc import NoResultFound
from ..exceptions import PermissionError

def check_perm(user_id, permission_code):
    """
        Checks whether a user has permission to perform an action.
        The permission_code parameter should be a permission contained in tPerm.

        If the user does not have permission to perfom an action, a permission
        error is thrown.
    """
    try:
        perm = db.DBSession.query(Perm).filter(Perm.perm_code==permission_code).one()
    except NoResultFound:
        raise PermissionError("No permission %s"%(permission_code))


    try:
        res = db.DBSession.query(User).join(RoleUser, RoleUser.user_id==User.id).\
            join(Perm, Perm.perm_id==perm.perm_id).\
            join(RolePerm, RolePerm.perm_id==Perm.perm_id).filter(User.id==user_id).one()
    except NoResultFound:
        raise PermissionError("Permission denied. User %s does not have permission %s"%
                        (user_id, permission_code))
