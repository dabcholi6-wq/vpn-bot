const { Telegraf, Markup } = require('telegraf');
const sqlite3 = require('sqlite3').verbose();

const TOKEN = '8415084076:AAFUuWgyOGXK3aFv5zp9ILwMRKSdcV8TtYI';
const ADMIN_ID = 7744236569;

// ========== دیتابیس ==========
const db = new sqlite3.Database('vpn_bot.db');

db.run(`CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    role TEXT DEFAULT 'user',
    wallet INTEGER DEFAULT 0,
    uuid TEXT,
    expire_date TEXT,
    used_traffic INTEGER DEFAULT 0,
    config_link TEXT
)`);

const bot = new Telegraf(TOKEN);

// اضافه کردن مدیر با کیف پول پر
db.get("SELECT * FROM users WHERE user_id = ?", [ADMIN_ID], (err, row) => {
    if (!row) {
        db.run("INSERT INTO users (user_id, role, wallet) VALUES (?, ?, ?)", [ADMIN_ID, 'admin', 100000000000]);
    }
});

// ========== دکمه‌ها ==========
function mainKeyboard() {
    return Markup.inlineKeyboard([
        [Markup.button.callback('🛒 خرید کانفیگ', 'buy')],
        [Markup.button.callback('💰 کیف پول', 'wallet')],
        [Markup.button.callback('📊 وضعیت کانفیگ', 'status')],
        [Markup.button.callback('👤 پروفایل', 'profile')]
    ]);
}

// ========== استارت ==========
bot.start((ctx) => {
    const userId = ctx.from.id;
    db.run("INSERT OR IGNORE INTO users (user_id) VALUES (?)", [userId]);
    
    ctx.replyWithHTML(
        'سلام کیری\nبه کصکش ترین ربات فیلتر شکن فروشی خوش آمدید',
        mainKeyboard()
    );
});

// ========== خرید ==========
bot.action('buy', (ctx) => {
    ctx.answerCbQuery();
    ctx.editMessageText(
        'گیگ: ۱۰ گیگ\nچند روزه: ۳۰ روزه\nتاریخ انقضا: ۳۰ روز بعد\nمبلغ: ۵۰,۰۰۰ تومان\n\nاگر می‌خوای بخری انگشت کیری‌ات رو روی دکمه زیر لمس کن',
        Markup.inlineKeyboard([
            [Markup.button.callback('خرید کانفیگ', 'confirm_buy')]
        ])
    );
});

// ========== تایید خرید ==========
bot.action('confirm_buy', (ctx) => {
    const userId = ctx.from.id;
    db.get("SELECT wallet FROM users WHERE user_id = ?", [userId], (err, row) => {
        if (!row || row.wallet < 50000) {
            ctx.editMessageText('بیااااااااا🖕\nبرو کیف پولت رو شارژ کن کصکش');
            return;
        }
        
        const expire = new Date();
        expire.setDate(expire.getDate() + 30);
        const expireStr = expire.toISOString().split('T')[0];
        
        db.run("UPDATE users SET wallet = wallet - 50000, uuid = ?, expire_date = ?, config_link = ? WHERE user_id = ?", 
            ['test-uuid-123', expireStr, 'vless://test@example.com:443', userId]);
        
        ctx.editMessageText(
            `✅ کانفیگ خریداری شد!\n\nگیگ: ۱۰ گیگ\nچند روزه: ۳۰ روزه\nتاریخ انقضا: ${expireStr}\nمبلغ پرداختی: ۵۰,۰۰۰ تومان\n\nلینک کانفیگ:\nvless://test@example.com:443`
        );
    });
});

// ========== کیف پول ==========
bot.action('wallet', (ctx) => {
    const userId = ctx.from.id;
    db.get("SELECT wallet FROM users WHERE user_id = ?", [userId], (err, row) => {
        const walletText = !row || row.wallet <= 0 ? '🖕' : `${row.wallet.toLocaleString()} تومان`;
        ctx.editMessageText(
            `حساب: ${userId}\nموجودی کیف پول: ${walletText}`,
            Markup.inlineKeyboard([
                [Markup.button.callback('شارژ کیف پول', 'charge')]
            ])
        );
    });
});

// ========== شارژ ==========
bot.action('charge', (ctx) => {
    ctx.editMessageText(
        'شماره کارت\n6219861439976183\nکریم جاهدی\n\nعکس رسید بفرست'
    );
});

// ========== وضعیت ==========
bot.action('status', (ctx) => {
    const userId = ctx.from.id;
    db.get("SELECT uuid, expire_date, used_traffic FROM users WHERE user_id = ?", [userId], (err, row) => {
        if (!row || !row.uuid) {
            ctx.editMessageText('❌ کانفیگ فعالی نداری کیری\nبرو یه کانفیگ بخر');
            return;
        }
        
        const now = new Date();
        const expire = new Date(row.expire_date);
        const daysLeft = Math.max(0, Math.floor((expire - now) / (1000 * 60 * 60 * 24)));
        
        ctx.editMessageText(
            `مقدار کانفیگ خریدی: ۱۰ گیگ\nچند روز مانده: ${daysLeft} روز\nمقدار سوپر دانلود شده: ${row.used_traffic} گیگ`
        );
    });
});

// ========== پروفایل ==========
bot.action('profile', (ctx) => {
    const userId = ctx.from.id;
    db.get("SELECT role, wallet, uuid FROM users WHERE user_id = ?", [userId], (err, row) => {
        if (!row) {
            ctx.editMessageText('❌ ثبت‌نام نکردی کیری!');
            return;
        }
        ctx.editMessageText(
            `👤 پروفایل\nآیدی: ${userId}\nنقش: ${row.role === 'admin' ? '👑 ادمین' : 'کاربر عادی'}\nموجودی: ${row.wallet.toLocaleString()} تومان\nوضعیت: ${row.uuid ? '✅ فعال' : '❌ بدون کانفیگ'}`
        );
    });
});

// ========== رسید عکس ==========
bot.on('photo', (ctx) => {
    const userId = ctx.from.id;
    ctx.reply('واستا کیری\nادمین ها باید قبول کنن');
    
    ctx.telegram.sendMessage(ADMIN_ID, 
        `یک کیری آیدی ${userId} واست پول زده قبول میکنی یا نه`,
        Markup.inlineKeyboard([
            [
                Markup.button.callback('آره', `accept_${userId}`),
                Markup.button.callback('نه', `reject_${userId}`)
            ]
        ])
    );
});

// ========== قبول کردن ==========
bot.action(/accept_(.+)/, (ctx) => {
    const userId = parseInt(ctx.match[1]);
    db.run("UPDATE users SET wallet = wallet + 50000 WHERE user_id = ?", [userId]);
    ctx.editMessageText(`✅ کیف پول کاربر ${userId} شارژ شد کیری`);
    ctx.telegram.sendMessage(userId, '✅ کیف پولت شارژ شد کیری');
});

// ========== رد کردن ==========
bot.action(/reject_(.+)/, (ctx) => {
    const userId = parseInt(ctx.match[1]);
    ctx.editMessageText(`❌ رد شدی کصکش، برو گریه کن`);
    ctx.telegram.sendMessage(userId, '❌ رد شدی کصکش، برو گریه کن');
});

// ========== راه‌اندازی ==========
bot.launch().then(() => {
    console.log('ربات روشن شد ✅');
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
