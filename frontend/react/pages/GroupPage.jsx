import React, { useEffect, useState } from "react";
import RestaurantCard from "../components/RestaurantCard.jsx";

const GroupsPage = () => {
  const [groups, setGroups] = useState([]);
  const [loadingGroups, setLoadingGroups] = useState(true);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [newGroupRestaurant, setNewGroupRestaurant] = useState("");
  const [restaurants, setRestaurants] = useState([]);
  const [selectedGroupId, setSelectedGroupId] = useState(null);
  const [groupDetails, setGroupDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [memberNetid, setMemberNetid] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [debounceId, setDebounceId] = useState(null);
  const [groupPreferences, setGroupPreferences] = useState(null);
  const [loadingPreferences, setLoadingPreferences] = useState(false);

  // Fetch user groups
  const loadGroups = async () => {
    setLoadingGroups(true);
    try {
      const res = await fetch('/api/groups');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setGroups(data.groups || []);
    } catch (e) {
      setError('Failed to load groups');
    } finally {
      setLoadingGroups(false);
    }
  };

  // Fetch restaurants for selection
  const loadRestaurants = async () => {
    try {
      const res = await fetch('/api/home');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setRestaurants(data.restaurants || []);
    } catch (e) {
      console.error('Failed to load restaurants', e);
    }
  };

  useEffect(() => {
    loadGroups();
    loadRestaurants();
  }, []);

  // Load group details
  const loadGroupDetails = async (groupId) => {
    setSelectedGroupId(groupId);
    setLoadingDetails(true);
    setGroupPreferences(null);
    try {
      const res = await fetch(`/api/groups/${groupId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setGroupDetails(data.group);
      // Load preferences
      loadGroupPreferences(groupId);
    } catch (e) {
      setActionMessage('Failed to load group');
      setGroupDetails(null);
    } finally {
      setLoadingDetails(false);
    }
  };

  // Load group preferences
  const loadGroupPreferences = async (groupId) => {
    setLoadingPreferences(true);
    try {
      const res = await fetch(`/api/groups/${groupId}/preferences`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setGroupPreferences(data.preferences);
    } catch (e) {
      console.error('Failed to load preferences', e);
      setGroupPreferences(null);
    } finally {
      setLoadingPreferences(false);
    }
  };

  const isLeader = () => {
    if (!groupDetails) return false;
    const username = groupDetails.members.find(m => m.role === 'leader');
    return true;
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    setActionMessage("");
    if (!newGroupName.trim()) {
      setActionMessage('Group name required');
      return;
    }
    try {
      const res = await fetch('/api/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ group_name: newGroupName.trim(), selected_restaurant_id: newGroupRestaurant || null })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to create group');
      setActionMessage('Group created');
      setShowCreate(false);
      setNewGroupName('');
      setNewGroupRestaurant('');
      loadGroups();
      loadGroupDetails(data.group.id);
    } catch (e) {
      setActionMessage(e.message);
    }
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    if (!memberNetid.trim()) {
      setActionMessage('NetID required');
      return;
    }
    try {
      const res = await fetch(`/api/groups/${selectedGroupId}/members`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ netid: memberNetid.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to add member');
      setActionMessage('Member added');
      setMemberNetid('');
      // Refresh details and preferences to reflect changes without reload
      await loadGroupDetails(selectedGroupId);
      await loadGroupPreferences(selectedGroupId);
      await loadGroups();
    } catch (e) {
      setActionMessage(e.message);
    }
  };

  // Debounced search for users by name/netid
  useEffect(() => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setSearchResults([]);
      setSearchError("");
      return;
    }
    if (debounceId) {
      clearTimeout(debounceId);
    }
    const id = setTimeout(async () => {
      setSearchLoading(true);
      try {
        const res = await fetch(`/api/users/search?q=${encodeURIComponent(searchQuery.trim())}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setSearchResults(data.users || []);
        setSearchError("");
      } catch (e) {
        setSearchError('Search failed');
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    }, 300);
    setDebounceId(id);
    return () => clearTimeout(id);
  }, [searchQuery]);

  const handleSelectSearchUser = async (user) => {
    if (!selectedGroupId) return;
    if (groupDetails && groupDetails.members.some(m => m.netid === user.netid)) {
      setActionMessage('User already in group');
      return;
    }
    try {
      const res = await fetch(`/api/groups/${selectedGroupId}/members`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ netid: user.netid })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to add');
      setGroupDetails(data.group);
      setActionMessage(`Added ${user.netid}`);
      setSearchQuery("");
      setSearchResults([]);
    } catch (e) {
      setActionMessage(e.message);
    }
  };

  const handleRemoveMember = async (netid) => {
    try {
      const res = await fetch(`/api/groups/${selectedGroupId}/members/${netid}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to remove member');
      setActionMessage('Member removed');
      // Refresh details and preferences to reflect changes
      await loadGroupDetails(selectedGroupId);
      await loadGroupPreferences(selectedGroupId);
      await loadGroups();
    } catch (e) {
      setActionMessage(e.message);
    }
  };

  const handleSetRestaurant = async (e) => {
    const restId = e.target.value;
    if (!restId) return;
    try {
      const res = await fetch(`/api/groups/${selectedGroupId}/restaurant`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ restaurant_id: restId })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to set restaurant');
      setActionMessage('Restaurant selected');
      await loadGroupDetails(selectedGroupId);
      await loadGroupPreferences(selectedGroupId);
      await loadGroups();
    } catch (e) {
      setActionMessage(e.message);
    }
  };

  const handleClearRestaurant = async () => {
    try {
      const res = await fetch(`/api/groups/${selectedGroupId}/restaurant`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ restaurant_id: null })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to clear restaurant');
      setActionMessage('Restaurant selection cleared');
      await loadGroupDetails(selectedGroupId);
      await loadGroupPreferences(selectedGroupId);
      await loadGroups();
    } catch (e) {
      setActionMessage(e.message);
    }
  };

  return (
    <div className="container mt-4">
      <h2 className="mb-3">Groups</h2>
      {error && <div className="alert alert-danger py-2 my-2">{error}</div>}
      {actionMessage && <div className="alert alert-info py-2 my-2">{actionMessage}</div>}

      <div className="d-flex justify-content-between align-items-center mb-3">
        <button className="btn" onClick={() => setShowCreate(s => !s)} style={{ backgroundColor: "#FF5F0D" }}>
          {showCreate ? 'Cancel' : '+ Create New Group'}
        </button>
      </div>

      {showCreate && (
        <form className="card card-body mb-4" onSubmit={handleCreateGroup}>
          <div className="mb-3">
            <label className="form-label">Group Name</label>
            <input className="form-control" value={newGroupName} onChange={e => setNewGroupName(e.target.value)} />
          </div>
          <div className="mb-3">
            <label className="form-label">Initial Restaurant (optional)</label>
            <select className="form-select" value={newGroupRestaurant} onChange={e => setNewGroupRestaurant(e.target.value)}>
              <option value="">-- None --</option>
              {restaurants.map(r => (
                <option key={r.id} value={r.id}>{r.name}</option>
              ))}
            </select>
          </div>
          <button type="submit" className="btn btn-success">Create Group</button>
        </form>
      )}

      <div className="row">
        <div className="col-md-5">
          <h5>Your Groups</h5>
          {loadingGroups && <p>Loading groups...</p>}
          {!loadingGroups && groups.length === 0 && (
            <p className="text-muted fst-italic">You are not part of any groups yet.</p>
          )}
          <ul className="list-group">
            {groups.map(g => (
              <li key={g.id} className={`list-group-item d-flex justify-content-between align-items-center ${selectedGroupId === g.id ? 'active' : ''}`}
                  style={{ cursor: 'pointer'}}
                  onClick={() => loadGroupDetails(g.id)}>
                <span >{g.group_name}</span>
                {g.selected_restaurant_id && (
                  <small className="badge bg-light text-dark">
                    {(() => {
                      const r = restaurants.find(r => String(r.id) === String(g.selected_restaurant_id));
                      return r ? r.name : 'Restaurant';
                    })()}
                  </small>
                )}
              </li>
            ))}
          </ul>
        </div>
        <div className="col-md-7 mt-4 mt-md-0">
          {loadingDetails && <p>Loading group details...</p>}
          {!loadingDetails && groupDetails && (
            <div className="card">
              <div className="card-body">
                <h4 className="card-title">{groupDetails.group_name}</h4>
                
                {/* Group Preferences Section */}
                {groupPreferences && (
                  <div className="mb-4 p-3 bg-light rounded">
                    <h6 className="mb-2">Group Preferences</h6>
                    <div className="mb-2">
                      <strong>Recommended Cuisines:</strong>{' '}
                      {groupPreferences.recommended_cuisines.length > 0 ? (
                        groupPreferences.recommended_cuisines.map((c, i) => (
                          <span key={i} className="badge me-1" style={{ backgroundColor: "#FF5F0D" }}>{c}</span>
                        ))
                      ) : (
                        <span className="text-muted fst-italic">No preferences yet</span>
                      )}
                    </div>
                    <div className="mb-2">
                      <strong>Dietary Restrictions:</strong>{' '}
                      {groupPreferences.dietary_restrictions.length > 0 ? (
                        groupPreferences.dietary_restrictions.map((d, i) => (
                          <span key={i} className="badge me-1" style={{ backgroundColor: "#FF5F0D" }}>{d}</span>
                        ))
                      ) : (
                        <span className="text-muted fst-italic">None</span>
                      )}
                    </div>
                    <div>
                      <strong>Allergies:</strong>{' '}
                      {groupPreferences.allergies.length > 0 ? (
                        groupPreferences.allergies.map((a, i) => (
                          <span key={i} className="badge me-1" style={{ backgroundColor: "#FF5F0D" }}>{a}</span>
                        ))
                      ) : (
                        <span className="text-muted fst-italic">None</span>
                      )}
                    </div>
                  </div>
                )}
                {loadingPreferences && <p className="text-muted fst-italic">Loading preferences...</p>}

                {/* Recommended matches section: show compact restaurant cards matching recommended cuisines */}
                {groupPreferences && restaurants && restaurants.length > 0 && (
                  (() => {
                    const recs = (groupPreferences.recommended_cuisines || []).map(c => c.trim().toLowerCase());
                    const matches = restaurants.filter(r => {
                      const cat = (r.category || '').trim().toLowerCase();
                      return cat && recs.includes(cat);
                    });
                    if (matches.length === 0) {
                      return (
                        <div className="mb-4">
                          <h6 className="mb-2">Recommended Matches</h6>
                          <p className="text-muted fst-italic">No matching restaurants for recommended cuisines yet.</p>
                        </div>
                      );
                    }
                    return (
                      <div className="mb-4">
                        <h6 className="mb-2">Recommended Matches</h6>
                        <div className="row g-3">
                          {matches.map(rest => (
                            <div key={rest.id} className="col-md-4 col-sm-6">
                              <RestaurantCard rest={rest} compact={true} />
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })()
                )}

                <div className="mb-3">
                  <label className="form-label">Selected Restaurant</label>
                  <select className="form-select" disabled={!isLeader()} value={groupDetails.selected_restaurant_id || ''} onChange={handleSetRestaurant}>
                    <option value="">-- Choose Restaurant --</option>
                    {restaurants.map(r => (
                      <option key={r.id} value={r.id}>{r.name}</option>
                    ))}
                  </select>
                  {groupDetails.selected_restaurant_id && (
                    <button
                      className="btn btn-outline-secondary btn-sm mt-2"
                      onClick={handleClearRestaurant}
                      disabled={!isLeader()}
                    >
                      Clear Selection
                    </button>
                  )}
                </div>

                <h5>Members</h5>
                <ul className="list-group mb-3">
                  {groupDetails.members.map(m => (
                    <li key={m.netid} className="list-group-item d-flex justify-content-between align-items-center">
                      <span>{m.fullname || m.firstname || m.netid} {m.role === 'leader' && <span className="badge ms-2" style={{ backgroundColor: "#FF5F0D" }}>Leader</span>}</span>
                      {m.role !== 'leader' && (
                        <button className="btn btn-sm btn-outline-danger" onClick={() => handleRemoveMember(m.netid)}>Remove</button>
                      )}
                    </li>
                  ))}
                </ul>
                <div className="mb-3">
                  <label className="form-label">Add Member (search by name or NetID)</label>
                  <input
                    className="form-control"
                    placeholder="Type at least 2 characters"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                  />
                  {searchLoading && <small className="text-muted">Searching...</small>}
                  {searchError && <div className="text-danger small">{searchError}</div>}
                  {searchResults.length > 0 && (
                    <ul className="list-group mt-2">
                      {searchResults.map(u => {
                        const inGroup = groupDetails.members.some(m => m.netid === u.netid);
                        return (
                          <li key={u.netid} className="list-group-item d-flex justify-content-between align-items-center">
                            <span>
                              {u.fullname || u.firstname || u.netid}
                              <small className="text-muted ms-2">{u.netid}</small>
                              {inGroup && <span className="badge bg-secondary ms-2">In group</span>}
                            </span>
                            {!inGroup && (
                              <button className="btn btn-sm btn-outline-primary" onClick={() => handleSelectSearchUser(u)}>Add</button>
                            )}
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          )}
          {!loadingDetails && !groupDetails && selectedGroupId && (
            <p className="text-danger">Failed to load group details.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default GroupsPage;
