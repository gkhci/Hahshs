let socket = io();
let token = localStorage.getItem('token');

// احراز هویت
if (!token) {
    window.location.href = '/login';
}

// اتصال وب‌سوکت
socket.on('connect', () => {
    console.log('✅ Connected to WebSocket');
});

socket.on('traffic_update', (data) => {
    updateTrafficChart(data);
});

// دریافت آمار
async function loadStats() {
    try {
        const response = await fetch('/api/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        
        document.getElementById('totalUsers').textContent = data.total_users;
        document.getElementById('activeUsers').textContent = data.active_users;
        document.getElementById('totalTraffic').textContent = 
            (data.total_traffic / (1024**3)).toFixed(2) + ' GB';
        document.getElementById('inboundsCount').textContent = data.inbounds_count;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// دریافت لیست کاربران
async function loadUsers() {
    try {
        const response = await fetch('/api/users', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const users = await response.json();
        
        const tbody = document.getElementById('usersBody');
        tbody.innerHTML = '';
        
        users.forEach(user => {
            const tr = document.createElement('tr');
            const used = (user.traffic_used / (1024**3)).toFixed(2);
            const limit = (user.traffic_limit / (1024**3)).toFixed(0);
            const expiry = new Date(user.expiry).toLocaleDateString('fa-IR');
            
            tr.innerHTML = `
                <td>${user.name}</td>
                <td>${used} GB</td>
                <td>${limit} GB</td>
                <td>${expiry}</td>
                <td><span class="badge bg-${user.status === 'active' ? 'success' : 'danger'}">${user.status}</span></td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteUser('${user.id}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// افزودن کاربر
async function addUser() {
    const name = document.getElementById('userName').value;
    const traffic = parseInt(document.getElementById('userTraffic').value);
    const days = parseInt(document.getElementById('userDays').value);
    
    if (!name) {
        alert('لطفاً نام کاربر را وارد کنید');
        return;
    }
    
    try {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, traffic_limit: traffic, expiry_days: days })
        });
        
        if (response.ok) {
            alert('✅ کاربر با موفقیت افزوده شد');
            document.getElementById('addUserModal').querySelector('.btn-close').click();
            loadStats();
            loadUsers();
        } else {
            alert('❌ خطا در افزودن کاربر');
        }
    } catch (error) {
        console.error('Error adding user:', error);
    }
}

// حذف کاربر
async function deleteUser(userId) {
    if (!confirm('آیا مطمئن هستید؟')) return;
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            alert('✅ کاربر حذف شد');
            loadStats();
            loadUsers();
        }
    } catch (error) {
        console.error('Error deleting user:', error);
    }
}

// خروج
function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

// نمایش مودال
function showAddUserModal() {
    const modal = new bootstrap.Modal(document.getElementById('addUserModal'));
    modal.show();
}

// بارگذاری اولیه
loadStats();
loadUsers();

// به‌روزرسانی خودکار هر ۳۰ ثانیه
setInterval(() => {
    loadStats();
    loadUsers();
}, 30000);
