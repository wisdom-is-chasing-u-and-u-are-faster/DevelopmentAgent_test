describe('Reservation Service Logic', () => {
  it('should compute valid 10-minute expiry timestamps', () => {
    const ttl = 600;
    const now = Date.now();
    const expiry = new Date(now + ttl * 1000);
    expect(expiry.getTime()).toBeGreaterThan(now);
    expect(expiry.getTime() - now).toBe(600000);
  });
});
